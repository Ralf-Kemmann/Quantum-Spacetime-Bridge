# BMS-FU02g5e1 - Near-Match Localization Field List

**Date:** 2026-05-08  
**Project:** Quantum-Spacetime Bridge / Gravitation und RaumZeit  
**Artifact:** Field list for FU02g5e1 config and outputs  
**Claim level:** combinatorial / methodological inspection only

---

## 1. Purpose

BMS-FU02g5e1 replays targeted raw-index windows and records all
role-colored near-match candidates under the v0 type-preferred diagnostic.

If exact FU02g4c enumeration order cannot be guaranteed from the available
inputs, the run must be labeled:

```text
scaffold localization
```

No physical emergence, uniqueness, or spacetime claim is made.

---

## 2. Config Fields

### `run.run_id`
**Type:** string  
**Description:** Stable identifier for this inspection run.

### `run.case_id`
**Type:** string  
**Description:** Human-readable case name.

### `run.output_dir`
**Type:** string / path  
**Description:** Output directory for candidate tables and result note.

### `run.mode_label`
**Type:** string  
**Description:** Must be `scaffold localization` unless exact FU02g4c replay order is guaranteed.

### `input.full_face_graph_edges_csv`
**Type:** string / path  
**Description:** C60 face adjacency CSV. Required endpoint columns are `face_a`, `face_b`.

### `input.reference_carrier_nodes`
**Type:** list[string]  
**Description:** FU02f1 reference carrier face labels.

### `input.reference_mixed_core_nodes`
**Type:** list[string]  
**Description:** FU02f1 reference mixed-core face labels.

### `input.reference_pentagon_boundary_nodes`
**Type:** list[string]  
**Description:** FU02f1 reference pentagon-boundary face labels.

### `near_signature.near_signature_max_abs_difference_sum`
**Type:** integer  
**Description:** Maximum role-signature absolute-difference sum counted as near.

### `windows[].window_id`
**Type:** string  
**Description:** Stable window identifier.

### `windows[].skip_first_raw_patches`
**Type:** integer  
**Description:** Zero-based raw patch index at which the window begins.

### `windows[].max_raw_patches_this_run`
**Type:** integer  
**Description:** Number of raw patches included in the window.

---

## 3. Output Fields - `near_match_candidates.csv`

### `window_id`
**Type:** string  
**Description:** Source window identifier.

### `raw_index`
**Type:** integer  
**Description:** Zero-based raw connected-patch index in the deterministic scaffold enumerator.

### `candidate_nodes`
**Type:** string  
**Description:** Semicolon-separated sorted candidate face labels.

### `exact_match`
**Type:** boolean  
**Description:** Whether the role-colored signature exactly equals the reference signature.

### `near_distance`
**Type:** integer  
**Description:** Role-colored absolute-difference distance to the reference signature.

### `role_colored_signature`
**Type:** string  
**Description:** v0 role-colored diagnostic signature string.

### `carrier_signature`
**Type:** string  
**Description:** Uncolored carrier diagnostic signature string.

### `internal_edge_count`
**Type:** integer  
**Description:** Number of internal adjacency edges induced by the candidate patch.

### `candidate_connected`
**Type:** boolean  
**Description:** Whether the candidate is connected in the supplied face graph.

### `h_count`
**Type:** integer  
**Description:** Number of hexagon-labeled candidate faces.

### `p_count`
**Type:** integer  
**Description:** Number of pentagon-labeled candidate faces.

### `warnings`
**Type:** string  
**Description:** Semicolon-separated candidate-level warnings.

---

## 4. Output Fields - `near_match_candidates.json`

JSON object containing run metadata, method boundary, summary counts, claim
boundary, and a `candidates` array with the same candidate records as
`near_match_candidates.csv`.

---

## 5. Result Note Sections

`result_note.md` must contain:

```text
Befund
Interpretation
Hypothese
Offene Luecke
Claim Boundary
```
