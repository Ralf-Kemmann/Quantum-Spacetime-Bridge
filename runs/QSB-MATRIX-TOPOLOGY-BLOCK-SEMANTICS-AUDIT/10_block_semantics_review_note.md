# QSB-MATRIX-TOPOLOGY-BLOCK-SEMANTICS-AUDIT

## Source basis

This review uses the EXTRACT03 edge-candidate file, the matrix topology closure-test component and degree summaries, and the prior block-structure audit outputs listed in `02_block_semantics_audit_scope.md`.

## Method

Each Pair-ID was parsed as integer `i|j`. The audit derived `delta`, `abs_delta`, orientation, and index interval fields for every node, then tested whether each confirmed clique block corresponds to exactly one absolute index-distance class. It also checked whether each class contains all directed Pair-IDs for that distance over the observed index interval and whether every unordered index pair has both orientations.

## Results

- Node count: 42
- Component count: 6
- Component sizes: [12, 10, 8, 6, 4, 2]
- Index interval: 0..6
- Indices present: [0, 1, 2, 3, 4, 5, 6]
- abs_delta values present: [1, 2, 3, 4, 5, 6]
- Component to abs_delta map: {'1': 1, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6}
- Covers all directed non-diagonal pairs: True
- All components single abs_delta: True
- Component sizes match `2*(index_count-d)`: True
- All components match distance rule: True
- All unordered pairs orientation-symmetric: True
- Orientation symmetric pair count: 21
- Orientation asymmetry count: 0
- Semantic status: `blocks_correspond_to_directed_pair_index_distance_classes`

## Interpretation

The complete disjoint clique blocks are not only abstract graph components under this audit. They correspond to directed Pair-ID distance classes `abs(i-j)=d` inside the observed index interval 0..6. The block sizes follow the internal index rule `2*(7-d)` for `d=1..6`.

This is an internal relational / index-semantic ordering of the candidate graph. It is not a physical, geometric, metric, gravitative, causal, dynamical, experimental, or physical-emergence interpretation.

## Claim boundary

The semantics described here are limited to Pair-ID parsing and graph/component membership over the audited files. This note makes no claim about physical geometry, spacetime, metric structure, gravitation, causality, dynamics, experimental validation, or physical emergence.

## Next-step gate

Any later use of the distance-class description should cite this run directory and preserve the index-semantic claim boundary. Further interpretation would require separate evidence and separate review.
