# EXTRACT03 Storage Semantics Correction Note

The initial numeric storage profile reported the core EXTRACT03 matrix CSV files as `1764x1`.

This describes the naive storage extraction, not the mathematical matrix semantics.

The inspected headers show long-form pair-pair matrix storage:

row_pair_id,column_pair_id,value,lineage_bundle_sha256

Therefore:

1764 rows = 42 x 42 pair-pair matrix entries

The edge-candidate artifact is stored separately as an off-diagonal pair-pair candidate table:

861 rows = 42 x 41 / 2 = choose(42, 2)

Observed semantic profile:

- K_candidate: 42x42 complete long-square pair-pair matrix
- distance_cost: 42x42 complete long-square pair-pair matrix
- shortest_path_D: 42x42 complete long-square pair-pair matrix
- relation_strength: 42x42 complete long-square pair-pair matrix
- edge_candidate: 861 off-diagonal pair-pair candidates
- edge candidate flags: 700 non-candidate, 161 candidate

Interpretation boundary:

- Storage shape must not be confused with semantic matrix shape.
- EXTRACT03 core matrices are eligible as 42x42 pair-pair relational matrix artifacts.
- The edge-candidate table supports off-diagonal candidate-edge review.
- This does not authorize geometry, physics, spacetime, metric, gravity, or causal claims by itself.
