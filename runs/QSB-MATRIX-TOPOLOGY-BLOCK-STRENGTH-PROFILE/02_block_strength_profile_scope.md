# QSB-MATRIX-TOPOLOGY-BLOCK-STRENGTH-PROFILE Scope

## Purpose

This run describes the numeric `strength` profile of the already confirmed Pair-ID distance-class block structure.

The guiding question is how edge strengths are distributed within and between the confirmed `abs(i-j)` blocks. The run is descriptive: it does not reinterpret the weights physically.

## Source basis

- `runs/QSB-EXTRACT03A-R1/authorized_execution_with_s1_addendum/16_edge_candidate_result.csv`
- `runs/QSB-MATRIX-TOPOLOGY-CLOSURE-TEST/04_closure_summary.json`
- `runs/QSB-MATRIX-TOPOLOGY-BLOCK-STRUCTURE-AUDIT/04_block_structure_summary.json`
- `runs/QSB-MATRIX-TOPOLOGY-BLOCK-SEMANTICS-AUDIT/04_block_semantics_summary.json`
- `runs/QSB-MATRIX-TOPOLOGY-BLOCK-SEMANTICS-AUDIT/05_pair_id_semantics_by_node.csv`
- `runs/QSB-MATRIX-TOPOLOGY-BLOCK-SEMANTICS-AUDIT/06_component_semantics_profile.csv`

## Checks

- Enrich each Pair-Pair edge row with component and `abs_delta` metadata.
- Separate rows within confirmed blocks from rows between confirmed blocks.
- Check whether all within-block rows are candidates and all between-block rows are non-candidates.
- Profile strength and threshold margins by component, component pair, abs-delta pair, and relation zone.
- List strongest internal and cross-block rows.

## Claim boundary

This run is purely structural, graph-theoretic, index-semantic, and numerically descriptive. It makes no claim about physical geometry, spacetime, metric structure, gravitation, causality, dynamics, experimental validation, or physical emergence. The `strength` values are treated only as numeric edge weights from the existing EXTRACT03 candidate logic.
