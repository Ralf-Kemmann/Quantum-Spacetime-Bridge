# BMS-FU02g5f - Raw-Order Replay Certification Field List

**Date:** 2026-05-08
**Project:** Quantum-Spacetime Bridge / Gravitation und RaumZeit
**Artifact:** Field list for FU02g5f config and outputs
**Claim level:** method/control block only

## Purpose

BMS-FU02g5f revalidates the FU02g5e1 near-match candidates against the repaired
C60 face graph and inspects `candidate_005` as a diagnostic stress case.

The block also records raw-order replay certification fields. If the runner
does not re-use the original FU02g4c enumerator and input bundle, raw-order
certification remains `not_certified`.

No physical emergence, spacetime emergence, global uniqueness, or global rarity
claim is made.

## Config Fields

### `run.run_id`
Stable run identifier.

### `run.case_id`
Human-readable case identifier.

### `run.output_dir`
Output directory for the generated FU02g5f artifacts.

### `run.reuses_original_fu02g4c_enumerator_input_bundle`
Boolean certification switch. Must be true only if this runner actually reuses
the original FU02g4c enumerator and input bundle. The supplied FU02g5f runner
sets this false.

### `input.full_face_graph_edges_csv`
Repaired C60 face adjacency CSV. Required columns: `face_a`, `face_b`.

### `input.near_match_candidates_csv`
FU02g5e1 near-match candidate table.

### `input.candidate_classification_csv`
FU02g5e2 classification table.

### `input.reference_carrier_nodes`
Reference carrier node set.

### `input.known_exact_localized_candidate_nodes`
Known exact localized candidate node set.

### `input.deep_inspection_candidate_id`
Candidate id selected for deep inspection. Default: `candidate_005`.

### `input.deep_inspection_raw_index`
Raw index expected for the deep-inspection candidate. Default: `26157530`.

## Output Fields - `summary.json`

### `metadata`
Run id, case id, timestamp, script path, and config path.

### `inputs`
Resolved input paths and configured reference/deep-inspection nodes.

### `raw_order_certification`
Certification status and basis fields:

- `raw_order_certification_status`
- `raw_order_certification_basis`
- `fu02g4c_order_guarantee`
- `scaffold_order_warning`

### `graph`
Full graph counts and reference induced-subgraph counts.

### `candidate_counts`
Aggregate counts for revalidated candidates.

### `candidate_005`
Summary of node, edge, signature, and isomorphism comparisons for
`candidate_005`.

### `outputs`
Paths to generated CSV, JSON, and Markdown artifacts.

### `claim_boundary`
Explicit methodological claim boundary and forbidden overclaims.

## Output Fields - `candidate_revalidation.csv`

### `candidate_id`
Candidate id from FU02g5e2, or deterministic row id if absent.

### `window_id`
Source FU02g5e1 window id.

### `raw_index`
Source raw index.

### `candidate_nodes`
Semicolon-separated sorted candidate node set.

### `candidate_node_count`
Recomputed candidate node count.

### `candidate_node_count_expected`
Reference node count.

### `candidate_node_count_ok`
Whether the candidate node count equals the reference node count.

### `candidate_edge_count`
Recomputed induced internal edge count.

### `source_internal_edge_count`
FU02g5e1 internal edge count, when available.

### `candidate_edge_count_ok`
Whether the recomputed edge count equals the source edge count when available.

### `candidate_connected`
Recomputed induced-subgraph connectedness.

### `source_candidate_connected`
FU02g5e1 connectedness value, when available.

### `h_count`
Recomputed hexagon-label count.

### `p_count`
Recomputed pentagon-label count.

### `source_h_count`
FU02g5e1 H count, when available.

### `source_p_count`
FU02g5e1 P count, when available.

### `uncolored_isomorphic_to_reference`
Recomputed uncolored graph-isomorphism flag.

### `face_type_preserving_isomorphic_to_reference`
Recomputed face-type-preserving graph-isomorphism flag.

### `mapping_count`
Number of face-type-preserving mappings from reference to candidate.

### `g5e2_uncolored_isomorphic_to_reference`
FU02g5e2 uncolored isomorphism value.

### `g5e2_face_type_preserving_isomorphic_to_reference`
FU02g5e2 face-type-preserving isomorphism value.

### `g5e2_mapping_count`
FU02g5e2 mapping count.

### `exact_match`
FU02g5e1 exact-match flag.

### `near_distance`
FU02g5e1 near-distance value. Treated as a coarse diagnostic only.

### `classification_primary`
FU02g5e2 primary classification, when available.

### `decision_basis`
Compact text basis for the revalidation decision.

### `raw_order_certification_status`
Raw-order certification status.

### `raw_order_certification_basis`
Basis for the raw-order certification status.

### `fu02g4c_order_guarantee`
Whether this runner guarantees FU02g4c raw order.

### `scaffold_order_warning`
Warning attached to scaffold-derived order.

### `warnings`
Semicolon-separated validation warnings.

## Output Fields - `candidate_005_node_diff.csv`

### `node`
Face node label.

### `diff_class`
One of `only_in_candidate_005`, `only_in_known_exact_candidate`, or
`in_both`.

### `face_type`
Face type inferred from label prefix.

## Output Fields - `candidate_005_edge_diff.csv`

### `edge_key`
Canonical `node_a--node_b` edge key.

### `node_a`
First sorted endpoint.

### `node_b`
Second sorted endpoint.

### `diff_class`
One of `only_in_candidate_005`, `only_in_known_exact_candidate`, or
`in_both`.

## Output Fields - `candidate_005_deep_inspection.csv`

Single-row diagnostic table comparing `candidate_005` against the known exact
candidate. It includes node-set differences, edge differences, degree
histograms, face-type counts, common coarse-signature components, isomorphism
flags, raw-order certification fields, and the near-distance interpretation.

## Output Fields - `isomorphism_audit.csv`

### `candidate_id`
Candidate id.

### `raw_index`
Source raw index.

### `candidate_node_count`
Recomputed node count.

### `candidate_edge_count`
Recomputed edge count.

### `candidate_connected`
Recomputed connectedness.

### `uncolored_isomorphic_to_reference`
Recomputed uncolored isomorphism flag.

### `face_type_preserving_isomorphic_to_reference`
Recomputed face-type-preserving isomorphism flag.

### `mapping_count`
Number of face-type-preserving mappings.

### `g5e2_agrees_uncolored`
Whether FU02g5e2 and FU02g5f agree on uncolored isomorphism.

### `g5e2_agrees_face_type_preserving`
Whether FU02g5e2 and FU02g5f agree on face-type-preserving isomorphism.

### `g5e2_agrees_mapping_count`
Whether FU02g5e2 and FU02g5f agree on mapping count.

### `audit_note`
Short audit interpretation.

## Output Fields - `result_note.md`

Required sections:

- Befund
- Interpretation
- Hypothese
- Offene Luecke
- Claim Boundary

The note must state whether raw-order replay certification was achieved,
whether `candidate_005` is a coarse-signature degeneracy case, that
`near_distance=0` is not equivalent to exact match or isomorphism, and that role
transport remains governed by the FU02g5c automorphy-only rule.
