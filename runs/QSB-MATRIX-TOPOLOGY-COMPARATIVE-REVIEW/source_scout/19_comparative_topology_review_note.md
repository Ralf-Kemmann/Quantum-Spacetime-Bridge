# QSB-MATRIX-TOPOLOGY-COMPARATIVE-REVIEW

## Review question

When does a filled matrix become a topologically load-bearing relational structure?

## Source basis

This review compares two already curated source sides:

1. D1K / RELALG synthetic topology-limit side
2. EXTRACT03 / pair-pair matrix candidate side

The primary source list and existence check are stored in:

- source_scout/10_curated_primary_sources_final.txt
- source_scout/11_curated_primary_sources_existence_check.csv

The raw profile and compact profile artifacts are stored in:

- source_scout/12_profile_extraction_raw.txt
- source_scout/13_compact_topology_profile.json
- source_scout/16_matrix_storage_semantic_profile.csv
- source_scout/17_storage_semantics_correction_note.md
- source_scout/18_comparative_topology_gate_table.csv

## D1K finding

D1K contains 9450 matched synthetic C-layer rows and 9450 directed relations.

The loop-min review reports:

- directed_edge_count = 9450
- unique_A_count = 1
- unique_B_count = 9450
- unique_node_count = 9451
- source_native_closed_triple_count = 0
- valid_loop_count = 0
- blocked_loop_count = 9450
- main blocked reason = missing_BC_relation
- star_like_topology_warning = true

Interpretation:

D1K is locally occupied and internally consistent as a synthetic diagnostic artifact, but its source-native topology is a one-center outgoing star. It does not provide source-native closed triples and does not support valid loops under the loop-min criterion.

Therefore D1K is used here as a topology-limit control case:

filled relation set does not imply relational closure.

## EXTRACT03 finding

The EXTRACT03 core matrix artifacts are stored as long-form pair-pair matrix tables.

The inspected storage semantics show:

- K_candidate: 1764 rows = 42x42 complete pair-pair matrix
- distance_cost: 1764 rows = 42x42 complete pair-pair matrix
- shortest_path_D: 1764 rows = 42x42 complete pair-pair matrix
- relation_strength: 1764 rows = 42x42 complete pair-pair matrix
- edge_candidate: 861 rows = choose(42,2) off-diagonal pair-pair candidates
- edge_candidate_flag_counts = 700 non-candidate, 161 candidate

Interpretation:

EXTRACT03 is not merely a list of occupied values. It provides complete square pair-pair matrix artifacts and a separate off-diagonal edge-candidate layer. This makes EXTRACT03 eligible for relational topology review.

This does not by itself authorize geometry, physics, spacetime, metric, gravity, or causal claims.

## Comparative result

D1K shows that a large, fully matched relation set can remain topologically non-closing when all source-native relations radiate from one center.

EXTRACT03 shows a different structural class: square pair-pair matrices with explicit off-diagonal edge candidates.

The comparative distinction is:

- D1K: filled source-star without source-native closure
- EXTRACT03: square pair-pair relational matrix candidate with candidate-edge support

## Gate criteria proposed

A matrix or relation set should not be called topologically load-bearing merely because it is large or filled.

Minimal criteria for relational topology eligibility:

1. semantic matrix shape must be explicit
2. source/target or row/column identifiers must support pair-pair comparison
3. closure candidates must be expressible
4. edge candidates must be distinguishable from mere stored values
5. loop or closed-triple tests must be performed before any loop-geometry claim
6. claim boundary must remain separate from visualization and storage format

## Claim boundary

This review supports only a structural/methodological conclusion:

Matrix occupancy is not sufficient for relational topology.
Semantic pair-pair organization and candidate-edge structure are necessary preconditions for topology review.

This review does not claim physical geometry, spacetime, metric, gravity, causality, or experimental validation.
