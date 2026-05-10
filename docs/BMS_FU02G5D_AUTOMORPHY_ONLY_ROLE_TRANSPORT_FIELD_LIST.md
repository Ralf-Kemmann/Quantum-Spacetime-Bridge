# BMS-FU02g5d - Automorphy-Only Role Transport Field List

**Date:** 2026-05-07  
**Project:** Quantum-Spacetime Bridge / Gravitation und RaumZeit  
**Artifact:** Field list for FU02g5d config and outputs  
**Claim level:** combinatorial / methodological control only

---

## 1. Purpose

BMS-FU02g5d checks whether `mixed_core` and `pentagon_boundary` roles may be
transported from the FU02f1 reference patch to a candidate patch under an
explicit isomorphism/automorphism witness.

Scientific rule:

```text
No mapping, no role transport.
Multiple mappings, report ambiguity.
No physical emergence, spacetime, uniqueness, or Lorentz claim.
```

---

## 2. Config Fields

### `run.run_id`
**Type:** string  
**Description:** Stable identifier for this FU02g5d run.

### `run.case_id`
**Type:** string  
**Description:** Human-readable case name for the automorphy-only check.

### `run.output_dir`
**Type:** string / path  
**Description:** Output directory for summary, mapping table, transported role sets, and result note.

### `input.full_face_graph_edges_csv`
**Type:** string / path  
**Description:** CSV edge list for the full C60 face graph. Required endpoint columns: `face_a`, `face_b`.

### `input.reference_carrier_nodes`
**Type:** list[string]  
**Description:** FU02f1 reference carrier face labels.

### `input.reference_mixed_core_nodes`
**Type:** list[string]  
**Description:** Reference faces carrying the `mixed_core` role.

### `input.reference_pentagon_boundary_nodes`
**Type:** list[string]  
**Description:** Reference faces carrying the `pentagon_boundary` role.

### `input.candidate_patch_nodes`
**Type:** list[string]  
**Description:** Candidate localized exact patch face labels.

---

## 3. Output Fields - `summary.json`

### `metadata.run_id`
**Type:** string  
**Description:** Run identifier copied from config.

### `metadata.case_id`
**Type:** string  
**Description:** Case identifier copied from config.

### `metadata.created_at_utc`
**Type:** string  
**Description:** UTC timestamp for the run.

### `input.full_face_graph_edges_csv`
**Type:** string  
**Description:** Source graph path used by the runner.

### `graph.full_node_count`
**Type:** integer  
**Description:** Number of nodes in the full face graph.

### `graph.full_edge_count`
**Type:** integer  
**Description:** Number of edges in the full face graph.

### `reference.node_count`
**Type:** integer  
**Description:** Number of reference carrier nodes.

### `reference.edge_count`
**Type:** integer  
**Description:** Number of induced reference-subgraph edges.

### `candidate.node_count`
**Type:** integer  
**Description:** Number of candidate patch nodes.

### `candidate.edge_count`
**Type:** integer  
**Description:** Number of induced candidate-subgraph edges.

### `isomorphism.mapping_count`
**Type:** integer  
**Description:** Number of face-type-preserving isomorphisms from reference induced subgraph to candidate induced subgraph.

### `isomorphism.mapping_exists`
**Type:** boolean  
**Description:** Whether at least one valid mapping exists.

### `role_transport.transport_allowed`
**Type:** boolean  
**Description:** True only when `mapping_count > 0`.

### `role_transport.unique_mixed_core_set_count`
**Type:** integer  
**Description:** Number of distinct transported mixed-core node sets across all mappings.

### `role_transport.unique_pentagon_boundary_set_count`
**Type:** integer  
**Description:** Number of distinct transported pentagon-boundary node sets across all mappings.

### `role_transport.mixed_core_invariant_across_mappings`
**Type:** boolean or null  
**Description:** True if all mappings transport the same mixed-core set; null when no mapping exists.

### `role_transport.pentagon_boundary_invariant_across_mappings`
**Type:** boolean or null  
**Description:** True if all mappings transport the same pentagon-boundary set; null when no mapping exists.

### `claim_boundary`
**Type:** object  
**Description:** Explicit negative claims: no physical emergence, spacetime, uniqueness, or Lorentz claim.

---

## 4. Output Fields - `mappings.csv`

### `mapping_index`
**Type:** integer  
**Description:** Zero-based mapping index.

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

## 5. Output Fields - `transported_role_sets.csv`

### `mapping_index`
**Type:** integer  
**Description:** Zero-based mapping index.

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

## 6. Result Note Sections

`result_note.md` must contain:

```text
Befund
Interpretation
Hypothese
Offene Luecke
Claim Boundary
```

