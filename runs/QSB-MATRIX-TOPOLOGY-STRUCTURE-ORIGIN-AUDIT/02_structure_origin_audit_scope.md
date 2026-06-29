# QSB-MATRIX-TOPOLOGY-STRUCTURE-ORIGIN-AUDIT Scope

## Purpose

This run audits whether the confirmed matrix-topology block structure is an additional downstream analysis property or whether it is constructively explained at artifact level by the candidate-edge rule.

The audit separates:

- data-level equivalence in the current `16_edge_candidate_result.csv` artifact,
- upstream trace evidence found in repo/run files,
- claim boundaries for any interpretation.

## Source basis

- `runs/QSB-EXTRACT03A-R1/authorized_execution_with_s1_addendum/16_edge_candidate_result.csv`
- `runs/QSB-MATRIX-TOPOLOGY-CLOSURE-TEST/04_closure_summary.json`
- `runs/QSB-MATRIX-TOPOLOGY-BLOCK-STRUCTURE-AUDIT/04_block_structure_summary.json`
- `runs/QSB-MATRIX-TOPOLOGY-BLOCK-SEMANTICS-AUDIT/04_block_semantics_summary.json`
- `runs/QSB-MATRIX-TOPOLOGY-BLOCK-STRENGTH-PROFILE/04_block_strength_summary.json`
- `runs/QSB-MATRIX-TOPOLOGY-BLOCK-NULLMODEL-AUDIT/04_nullmodel_summary.json`

## Checks

- Parse Pair-IDs and derive `abs_delta`.
- Test whether `edge_candidate_flag` is equivalent to shared `abs_delta`.
- Test whether `edge_candidate_flag` is equivalent to `strength >= theta_edge`.
- Test whether `strength == 1.0` is equivalent to shared `abs_delta`.
- Inventory upstream traces without turning text matches into unverified rule claims.
- Probe whether the exact `same abs_delta` explanation is tied to the current Pair-ID labels by deterministic label permutations.

## Claim boundary

This audit is purely methodical, structural, graph-theoretic, and data-lineage oriented. It makes no claim about physical geometry, spacetime, metric structure, gravitation, causality, dynamics, experimental validation, or physical emergence.
