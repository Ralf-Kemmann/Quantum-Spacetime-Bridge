# QSB Planck Bridge Resonator Matrix Construction Contract Design 01

## 1. Executive Summary

This run creates a reviewable Matrix Construction Contract draft for the QSB/PBR `K_candidate` construction.

`contract_design_status=draft_contract_ready_for_human_review`

The draft is based on the prior source-alignment result:

`alignment_status=partial_contract_found_requires_design_review`

No matrix was reconstructed. No spectral measurement, nullmodel, candidate repair, DWH write, literature import, or Lag-Class Sufficiency execution was performed.

## 2. Why This Contract Design Is Needed

The blocked Lag-Class Sufficiency execution stopped because a `K_candidate` export exists, but no standalone construction contract was available for future reconstruction and sufficiency gating.

This design answers what must be fixed before `K_candidate` can be reconstructed for Lag-Class Sufficiency: input identity, pair policy, lag handoff, matrix rule, validation policy, control eligibility, and a K-only callable must all be explicit.

## 3. Inputs Used and Limitations

Primary evidence source:

`runs/QSB-PLANCK-BRIDGE-RESONATOR-MATRIX-CONSTRUCTION-CONTRACT-SOURCE-ALIGNMENT-01/`

Required context inspected:

- `runs/QSB-PLANCK-BRIDGE-RESONATOR-LAG-CLASS-SUFFICIENCY-EXECUTION-01/`
- `runs/QSB-PLANCK-BRIDGE-RESONATOR-LAG-CLASS-SUFFICIENCY-DESIGN-01/`
- `runs/QSB-PLANCK-BRIDGE-RESONATOR-INDEPENDENT-LAG-VARIABLE-ADMISSIBILITY-CLOSURE-REVIEW-01/`

Context-only runs were detected but not used as internal evidence for K construction.

Limitation: the draft still contains `missing_not_documented` fields. Those fields are intentionally not invented.

## 4. Evidence Status Vocabulary

Allowed evidence statuses:

- `documented_existing_evidence`
- `derived_from_existing_code_trace`
- `partial_evidence_requires_review`
- `missing_not_documented`
- `not_applicable`

## 5. Contract Draft Overview

The design separates known source-lineage facts from code-derived behavior and missing contract fields. It is ready for human review, not execution.

## 6. Contract Sections C0-C9

### C0 - Contract metadata

See `data/contract_metadata.csv`.

Draft contract ID: `QSB-PBR-K-CANDIDATE-MATRIX-CONSTRUCTION-CONTRACT-DRAFT-01`.

### C1 - Source and lineage

See `data/source_lineage_contract.csv`.

The historical code source and K export hash are documented. Lineage remains review-gated because the source is distributed across code and output artifacts.

### C2 - Input tables and identity

See `data/input_identity_contract.csv`.

Pair identifiers and endpoint fields are evidenced. Duplicate and missing row policies remain undocumented.

### C3 - Pair and diagonal policy

See `data/pair_diagonal_policy_contract.csv`.

Ordered non-diagonal pair policy is evidenced. Symmetrization and diagonal fill are code-derived and require review as contract text.

### C4 - Lag policy

See `data/lag_policy_contract.csv`.

Lag handoff remains the major missing area. No lag value column, class column, class definition, cardinality source, sort order, shuffle definition, or alias exclusion rule is documented as a K construction contract field.

### C5 - Matrix construction rule

See `data/matrix_construction_rule_contract.csv`.

The K entry formula is documented as normalized-vector dot product. Aggregation and symmetrization are derived from the EXTRACT03A-R1 code trace.

### C6 - Numerical and validation policy

See `data/numerical_validation_policy_contract.csv`.

Finite/shape/symmetry/diagonal/PSD/range checks are evidenced. Rank and metric policies remain missing.

### C7 - Randomization and controls eligibility

See `data/randomization_controls_eligibility.csv`.

All controls remain review-gated or missing because the lag handoff and randomization policy are not yet contractually fixed.

### C8 - Reconstruction command / callable

See `data/reconstruction_callable_contract.csv`.

A standalone K-only callable is missing. The historical EXTRACT03A-R1 runner is not accepted here as a final callable contract.

### C9 - Human review checklist

See `data/human_review_checklist.csv`.

The checklist turns all blocking gaps into explicit review questions.

## 7. Evidence Map

See `data/contract_component_evidence_map.csv`.

Key evidence:

- EXTRACT03A-R1 runner path and hash.
- K export path and hash.
- S1 pair basis review.
- EXTRACT03A-R1 runtime mapping.
- EXTRACT03A-R1 K validation.
- Source-alignment gap analysis.

## 8. Gaps and Patch Requirements

See `data/source_patch_requirements.csv`.

Minimum required patch/design items:

- K-only reconstruction callable.
- Direct input identity export or pinned source table contract.
- Duplicate/missing row and pair policies.
- Lag-class derivation and join policy.
- Rank/metric policy.
- Randomization/control policy.

## 9. Human Review Checklist

The review checklist is blocking. A reviewer must approve or revise the draft before any execution use.

## 10. Future Execution Unblock Criteria

See `data/future_execution_unblock_criteria.csv`.

All required criteria must pass before any Lag-Class Sufficiency execution can be reconsidered.

## 11. Claim Boundaries

`physical_claim_release=blocked_no_physics_claim`

`mechanism_claim_release=blocked_no_mechanism_claim`

This run makes no physical emergence, spacetime, gravity, Lorentz, dynamics, uniqueness, rarity, mechanism, or sufficiency claim.

## 12. German Claim-Safe Summary

Dieser Matrix-Construction-Contract-Design-Run erstellt einen reviewbaren Vertragsentwurf fuer die Rekonstruktion der QSB/PBR-K_candidate-Matrix aus den vorhandenen technischen Spuren, insbesondere EXTRACT03A-R1. Der Run trennt belegte Vertragsbestandteile, aus Code-Spuren ableitbare Bestandteile, reviewpflichtige Teilbelege und fehlende Komponenten. Er rekonstruiert keine Matrix, berechnet keine Spektren, fuehrt keinen Lag-Class-Sufficiency-Test aus und erzeugt keine neue Matrixregel. Physikalische Claims und Mechanismusclaims bleiben gesperrt.

