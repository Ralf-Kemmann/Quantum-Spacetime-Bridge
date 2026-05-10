# BMS-FU02g5e2 - Near-Match Decoy Classification Field List

**Date:** 2026-05-08  
**Project:** Quantum-Spacetime Bridge / Gravitation und RaumZeit  
**Artifact:** Field list for FU02g5e2 config and outputs  
**Claim level:** combinatorial / methodological classification only

---

## 1. Purpose

BMS-FU02g5e2 classifies the near-match candidates localized by
BMS-FU02g5e1. It compares every candidate induced subgraph against the
reference induced subgraph and permits `mixed_core` / `pentagon_boundary` role
transport only through explicit face-type-preserving isomorphisms.

Scientific rule:

```text
No free role transport.
No face-type-preserving isomorphism, no reference role transport.
Multiple mappings, report ambiguity.
No physical emergence, spacetime emergence, global uniqueness, or FU02g4c
replay certification claim.
```

---

## 2. Config Fields

### `run.run_id`
**Type:** string  
**Description:** Stable identifier for this FU02g5e2 run.

### `run.case_id`
**Type:** string  
**Description:** Human-readable case name for the classification run.

### `run.output_dir`
**Type:** string / path  
**Description:** Output directory for summary, classification tables, mapping table, transported role sets, and result note.

### `run.mode_label`
**Type:** string  
**Description:** Provenance label. Default for this run is `g5e1 scaffold localization`.

### `run.scaffold_order_certification`
**Type:** boolean  
**Description:** All candidates inherit this value. Must remain false unless explicitly certified by config.

### `input.near_match_candidates_csv`
**Type:** string / path  
**Description:** FU02g5e1 near-match candidate CSV.

### `input.full_face_graph_edges_csv`
**Type:** string / path  
**Description:** C60 face adjacency CSV. Required endpoint columns are `face_a`, `face_b`.

### `input.reference_carrier_nodes`
**Type:** list[string]  
**Description:** Reference carrier face labels.

### `input.reference_mixed_core_nodes`
**Type:** list[string]  
**Description:** Reference faces carrying the `mixed_core` role.

### `input.reference_pentagon_boundary_nodes`
**Type:** list[string]  
**Description:** Reference faces carrying the `pentagon_boundary` role.

### `input.known_exact_localized_fu02g4c_candidate_nodes`
**Type:** list[string]  
**Description:** Known exact localized FU02g4c candidate node set used for the `known_exact_spiegelklunker` classification.

---

## 3. Output Fields - `summary.json`

### `metadata`
**Type:** object  
**Description:** Run id, case id, creation timestamp, script path, mode label, and scaffold-order certification state.

### `input`
**Type:** object  
**Description:** Config path and resolved input paths and reference node sets.

### `graph`
**Type:** object  
**Description:** Full graph and reference induced-subgraph counts.

### `summary_counts`
**Type:** object  
**Description:** Candidate count and aggregate counts by primary classification, mapping state, and role-transport invariance.

### `outputs`
**Type:** object  
**Description:** Paths to CSV, JSON, and Markdown artifacts created by this run.

### `claim_boundary`
**Type:** object  
**Description:** Explicit negative claims for physical emergence, spacetime emergence, global uniqueness, FU02g4c replay certification, and role transport without isomorphism.

---

## 4. Output Fields - `candidate_classification.csv`

### `candidate_id`
**Type:** string  
**Description:** Stable row identifier assigned by FU02g5e2.

### `window_id`
**Type:** string  
**Description:** Source FU02g5e1 window id.

### `raw_index`
**Type:** integer  
**Description:** Raw scaffold-localization index copied from FU02g5e1.

### `candidate_nodes`
**Type:** string  
**Description:** Semicolon-separated sorted candidate face labels.

### `exact_match`
**Type:** boolean  
**Description:** Exact role-signature flag copied from FU02g5e1.

### `near_distance`
**Type:** integer  
**Description:** Near-distance copied from FU02g5e1.

### `candidate_node_count`
**Type:** integer  
**Description:** Number of parsed candidate nodes.

### `candidate_edge_count`
**Type:** integer  
**Description:** Number of induced candidate-subgraph edges.

### `candidate_connected`
**Type:** boolean  
**Description:** Connectivity of the candidate induced subgraph in the supplied face graph.

### `uncolored_isomorphic_to_reference`
**Type:** boolean  
**Description:** Whether the reference and candidate induced subgraphs are isomorphic without face-type coloring.

### `face_type_preserving_isomorphic_to_reference`
**Type:** boolean  
**Description:** Whether at least one face-type-preserving isomorphism exists.

### `mapping_count`
**Type:** integer  
**Description:** Number of face-type-preserving mappings from reference to candidate.

### `role_transport_allowed`
**Type:** boolean  
**Description:** True only when `mapping_count > 0`.

### `unique_transported_mixed_core_set_count`
**Type:** integer  
**Description:** Number of distinct transported mixed-core node sets across valid mappings.

### `unique_transported_pentagon_boundary_set_count`
**Type:** integer  
**Description:** Number of distinct transported pentagon-boundary node sets across valid mappings.

### `mixed_core_transport_invariant`
**Type:** boolean or empty  
**Description:** True if all mappings transport the same mixed-core set; empty when no mapping exists.

### `pentagon_boundary_transport_invariant`
**Type:** boolean or empty  
**Description:** True if all mappings transport the same pentagon-boundary set; empty when no mapping exists.

### `classification_primary`
**Type:** string  
**Description:** Primary decoy classification assigned by the rule table.

### `classification_boundary`
**Type:** string  
**Description:** Always `scaffold_only_candidate_pending_fu02g4c_replay_validation`.

### `scaffold_order_certification`
**Type:** boolean  
**Description:** Candidate-level inherited scaffold-order certification flag.

### `warnings`
**Type:** string  
**Description:** Semicolon-separated validation warnings.

---

## 5. Output Fields - `candidate_mappings.csv`

### `candidate_id`
**Type:** string  
**Description:** Candidate row identifier.

### `mapping_index`
**Type:** integer  
**Description:** Zero-based mapping index within the candidate.

### `reference_node`
**Type:** string  
**Description:** Reference face label.

### `candidate_node`
**Type:** string  
**Description:** Candidate face label mapped from the reference node.

### `reference_face_type`
**Type:** string  
**Description:** Face type inferred from reference label: `H`, `P`, or `unknown`.

### `candidate_face_type`
**Type:** string  
**Description:** Face type inferred from candidate label: `H`, `P`, or `unknown`.

### `transported_role`
**Type:** string  
**Description:** `mixed_core`, `pentagon_boundary`, or `carrier_other`.

---

## 6. Output Fields - `transported_role_sets.csv`

### `candidate_id`
**Type:** string  
**Description:** Candidate row identifier.

### `mapping_index`
**Type:** integer  
**Description:** Zero-based mapping index within the candidate.

### `mixed_core_nodes`
**Type:** string  
**Description:** Semicolon-separated transported mixed-core candidate nodes.

### `pentagon_boundary_nodes`
**Type:** string  
**Description:** Semicolon-separated transported pentagon-boundary candidate nodes.

### `mixed_core_key`
**Type:** string  
**Description:** Stable sorted set key for the transported mixed-core nodes.

### `pentagon_boundary_key`
**Type:** string  
**Description:** Stable sorted set key for the transported pentagon-boundary nodes.

---

## 7. Result Note Sections

`result_note.md` must contain:

```text
Befund
Interpretation
Hypothese
Offene Luecke
Claim Boundary
```
