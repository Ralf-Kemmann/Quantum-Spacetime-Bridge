# QSB-MATRIX-TOPOLOGY-BLOCK-SEMANTICS-AUDIT Scope

## Purpose

This run performs a structural index-semantics audit of the six complete disjoint candidate-edge clique blocks confirmed in the block-structure audit.

The guiding question is what the six blocks mean at Pair-ID level, restricted to internal relational / index-based meaning inside the EXTRACT03 candidate graph.

## Source basis

- `runs/QSB-EXTRACT03A-R1/authorized_execution_with_s1_addendum/16_edge_candidate_result.csv`
- `runs/QSB-MATRIX-TOPOLOGY-CLOSURE-TEST/04_closure_summary.json`
- `runs/QSB-MATRIX-TOPOLOGY-CLOSURE-TEST/05_degree_summary.csv`
- `runs/QSB-MATRIX-TOPOLOGY-CLOSURE-TEST/06_component_summary.csv`
- `runs/QSB-MATRIX-TOPOLOGY-CLOSURE-TEST/07_triangle_candidates.csv`
- `runs/QSB-MATRIX-TOPOLOGY-BLOCK-STRUCTURE-AUDIT/04_block_structure_summary.json`
- `runs/QSB-MATRIX-TOPOLOGY-BLOCK-STRUCTURE-AUDIT/05_component_clique_audit.csv`
- `runs/QSB-MATRIX-TOPOLOGY-BLOCK-STRUCTURE-AUDIT/06_node_degree_expectation_audit.csv`

## Checks

- Parse each Pair-ID `i|j` into integer indices and derived fields.
- Test whether each component contains exactly one absolute index distance `abs(i-j)`.
- Test whether each component contains all directed Pair-IDs for its distance class over the observed global index interval.
- Test whether each unordered index pair has both orientations.
- Test whether observed Pair-IDs cover all non-diagonal directed pairs over the observed global index interval.

## Claim boundary

This audit is purely structural, graph-theoretic, and index-semantic. It makes no claim about physical geometry, spacetime, metric structure, gravitation, causality, dynamics, experimental validation, or physical emergence.
