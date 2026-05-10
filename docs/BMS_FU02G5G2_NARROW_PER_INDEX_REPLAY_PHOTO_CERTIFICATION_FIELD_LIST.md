# BMS-FU02g5g2 - Narrow Per-Index Replay/Photo Certification Field List

**Date:** 2026-05-09
**Project:** Quantum-Spacetime Bridge / Gravitation und RaumZeit
**Artifact:** Field list for FU02g5g2 config and outputs
**Claim level:** certification/control block only

## Purpose

BMS-FU02g5g2 attempts narrow per-index photo certification for the non-exact
near candidates from BMS-FU02g5e1/g5e2/g5f/g5g, with `candidate_005` as an
explicit coarse-signature degeneracy stress case and `candidate_008` as a
positive control.

The runner reconstructs the deterministic connected 17-face patch enumeration
used by the current scaffold/FU02g4c-style logic, captures patch photos at the
specified scaffold raw indices, and compares each captured node/edge set with
the FU02g5e1 expected candidate node set.

If the exact original FU02g4c enumerator and full original input bundle are not
reused, `full_fu02g4c_replay_certification` remains false.

## Status Distinctions

### `per_index_photo_agreement`
Direct agreement between the captured per-index photo and the expected candidate
node set.

### `scaffold_order_agreement`
The current scaffold/FU02g4c-style deterministic order reproduces the expected
node set at the requested index.

### `full_fu02g4c_replay_certification`
Full certification against the original FU02g4c enumerator and full input
bundle. This runner sets it false unless exact original reuse is explicitly
configured and supported.

## Config Fields

### `run.run_id`
Stable run identifier.

### `run.case_id`
Human-readable case id.

### `run.output_dir`
Output directory for generated artifacts.

### `run.target_patch_size`
Patch size to enumerate. Default target is 17.

### `run.max_runtime_seconds`
Stop limit for one-pass enumeration.

### `run.full_fu02g4c_replay_certification`
Must remain false unless the exact original FU02g4c enumerator and full input
bundle are reused.

### `run.index_semantics`
Documents that target raw indices are interpreted as the FU02g4c-style
`skip_first_raw_patches` count: skip `target_raw_index` patches, then capture
the next enumerated patch.

### `input.g5e1_candidates_csv`
FU02g5e1 near-match candidate table.

### `input.g5e2_classification_csv`
FU02g5e2 classification table.

### `input.g5f_revalidation_csv`
FU02g5f revalidation table.

### `input.g5g_replay_certification_csv`
FU02g5g candidate replay certification table.

### `input.face_graph_edges_csv`
FU02d1 repaired C60 face graph. Required endpoint columns: `face_a`, `face_b`.

### `input.reference_carrier_nodes`
Reference carrier nodes for isomorphism checks.

### `input.known_exact_localized_candidate_nodes`
Known exact localized candidate nodes.

### `targets`
Candidate ids and raw indices to photo.

## Output Fields - `summary.json`

### `metadata`
Run id, case id, timestamp, script path, and config path.

### `inputs`
Resolved input paths and configured targets.

### `runtime`
Enumeration strategy, stop reason, max target, and elapsed seconds.

### `certification_counts`
Counts by per-index photo status, node agreement, edge agreement, and full
FU02g4c certification flag.

### `candidate_005`
Explicit status summary for the coarse-signature degeneracy stress case.

### `candidate_008_positive_control`
Explicit status summary for the known exact positive control.

### `outputs`
Generated artifact paths.

### `claim_boundary`
Explicit negative-claim boundary.

## Output Fields - `per_index_photo_certification.csv`

### `candidate_id`
Target candidate id.

### `target_raw_index`
Requested scaffold/FU02g4c-style target index.

### `expected_candidate_nodes`
Semicolon-separated expected candidate node set from FU02g5e1.

### `replayed_candidate_nodes`
Semicolon-separated captured node set.

### `node_set_agreement`
Whether expected and captured node sets are identical.

### `edge_set_agreement`
Whether expected and captured induced edge sets are identical.

### `per_index_photo_status`
One of `matched_expected_nodes`, `node_mismatch`, `replay_not_attempted`,
`replay_failed`, or `timeout`.

### `prior_g5g_status`
Candidate-level FU02g5g status.

### `g5e2_classification_primary`
FU02g5e2 classification.

### `exact_match`
FU02g5e1 exact-match flag.

### `near_distance`
FU02g5e1 near-distance value.

### `uncolored_isomorphic_to_reference`
Recomputed uncolored isomorphism to the reference carrier.

### `face_type_preserving_isomorphic_to_reference`
Recomputed face-type-preserving isomorphism to the reference carrier.

### `mapping_count`
Number of face-type-preserving mappings.

### `role_transport_allowed_under_g5c`
True only when face-type-preserving mappings exist.

### `full_fu02g4c_replay_certification`
False unless exact original FU02g4c replay is certified.

### `certification_basis`
Text basis for the candidate-level photo status.

### `warnings`
Semicolon-separated candidate warnings.

## Output Fields - `per_index_node_photos.csv`

### `candidate_id`
Target candidate id.

### `target_raw_index`
Requested target index.

### `node`
Captured node label.

### `face_type`
Face type inferred from label prefix.

### `in_expected_candidate`
Whether the node is in the FU02g5e1 expected candidate set.

### `photo_status`
Candidate photo status.

## Output Fields - `per_index_edge_photos.csv`

### `candidate_id`
Target candidate id.

### `target_raw_index`
Requested target index.

### `edge_key`
Canonical `node_a--node_b` edge key.

### `node_a`
First sorted endpoint.

### `node_b`
Second sorted endpoint.

### `in_expected_edge_set`
Whether this edge is also in the expected candidate induced edge set.

### `photo_status`
Candidate photo status.

## Output Fields - `isomorphism_recheck.csv`

### `candidate_id`
Target candidate id.

### `target_raw_index`
Target raw index.

### `node_set_agreement`
Node-set agreement flag.

### `uncolored_isomorphic_to_reference`
Recomputed uncolored isomorphism flag.

### `face_type_preserving_isomorphic_to_reference`
Recomputed face-type-preserving isomorphism flag.

### `mapping_count`
Face-type-preserving mapping count.

### `g5e2_uncolored_isomorphic_to_reference`
Prior FU02g5e2 uncolored isomorphism flag.

### `g5e2_face_type_preserving_isomorphic_to_reference`
Prior FU02g5e2 face-type-preserving isomorphism flag.

### `g5e2_mapping_count`
Prior FU02g5e2 mapping count.

### `g5e2_agrees_uncolored`
Agreement between FU02g5g2 and FU02g5e2 for uncolored isomorphism.

### `g5e2_agrees_face_type_preserving`
Agreement between FU02g5g2 and FU02g5e2 for face-type-preserving isomorphism.

### `g5e2_agrees_mapping_count`
Agreement between FU02g5g2 and FU02g5e2 for mapping count.

## Output Fields - `result_note.md`

Required sections:

- Befund
- Interpretation
- Hypothese
- Offene Luecke
- Claim Boundary

The note states per-index photo agreement for each candidate, whether
`candidate_005` got a direct per-index photo, whether the `candidate_008`
positive control reproduced, whether full FU02g4c replay certification was
achieved, and that no physical or global uniqueness claim follows.
