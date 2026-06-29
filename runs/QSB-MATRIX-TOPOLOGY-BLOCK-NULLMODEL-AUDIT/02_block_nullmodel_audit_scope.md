# QSB-MATRIX-TOPOLOGY-BLOCK-NULLMODEL-AUDIT Scope

## Purpose

This run tests how unusual the confirmed complete disjoint clique-block structure is under specified graph-theoretic controls.

The run is statistical-descriptive only. It does not assign physical meaning to the observed structure.

## Source basis

- `runs/QSB-EXTRACT03A-R1/authorized_execution_with_s1_addendum/16_edge_candidate_result.csv`
- `runs/QSB-MATRIX-TOPOLOGY-CLOSURE-TEST/04_closure_summary.json`
- `runs/QSB-MATRIX-TOPOLOGY-BLOCK-STRUCTURE-AUDIT/04_block_structure_summary.json`
- `runs/QSB-MATRIX-TOPOLOGY-BLOCK-SEMANTICS-AUDIT/04_block_semantics_summary.json`
- `runs/QSB-MATRIX-TOPOLOGY-BLOCK-SEMANTICS-AUDIT/05_pair_id_semantics_by_node.csv`
- `runs/QSB-MATRIX-TOPOLOGY-BLOCK-SEMANTICS-AUDIT/06_component_semantics_profile.csv`
- Optional context if present: `runs/QSB-MATRIX-TOPOLOGY-BLOCK-STRENGTH-PROFILE/04_block_strength_summary.json`

## Nullmodels

- Fixed edge-count `G(n,m)` random graphs on the same 42 nodes and 861 possible edges, with exactly 161 edges.
- Degree-preserving double-edge-swap controls starting from the observed candidate graph.
- Semantic block randomization with fixed block sizes `[12,10,8,6,4,2]` and randomized node assignment.

## Claim boundary

This audit is purely structural, graph-theoretic, index-semantic, and statistically descriptive. Nullmodel results only describe rarity under the tested controls. They make no claim about physical geometry, spacetime, metric structure, gravitation, causality, dynamics, experimental validation, or physical emergence.
