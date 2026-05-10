# BMS-FU02g4c — Orbit-Reduced / Resumable Connected Patch Enumeration Field List

Date: 2026-05-03  
Project: Gravitation und RaumZeit / Quantum-Spacetime-Bridge  
Recommended repo target: `docs/BMS_FU02G4C_ORBIT_REDUCED_RESUMABLE_CONNECTED_PATCH_ENUMERATION_FIELD_LIST.md`

---

## 1. Purpose

This file documents the fields used by BMS-FU02g4c.

FU02g4c processes deterministic chunks of connected C60 face patches and optionally canonicalizes patches under face-type-preserving C60 face-graph automorphisms.

---

## 2. Config fields

| field name | type | description |
|---|---:|---|
| `run.run_id` | string | Stable run id. |
| `run.output_dir` | string | Output directory. |
| `run.chunk_id` | string | Human-readable chunk identifier. |
| `run.random_seed` | integer | Reserved seed; current enumeration is deterministic. |
| `inputs.c60_cells_csv` | string | C60 cell table. |
| `inputs.c60_edges_csv` | string | C60 edge table. |
| `inputs.fu02f1_face_layout_csv` | string | FU02f1 face role table. |
| `reference_roles.mixed_core_role` | string | FU02f1 label mapped to mixed core. |
| `reference_roles.pentagon_boundary_role` | string | FU02f1 label mapped to pentagon boundary. |
| `reference_roles.adjacent_shell_role` | string | FU02f1 label mapped to adjacent shell. |
| `reference_roles.noncarrier_role` | string | FU02f1 label mapped to noncarrier. |
| `enumeration.target_patch_size` | integer/string | Patch size or `reference`. |
| `enumeration.skip_first_raw_patches` | integer | Number of raw patches to skip before processing. |
| `enumeration.max_raw_patches_this_run` | integer | Maximum raw patches to process in this chunk. |
| `enumeration.timeout_seconds` | integer/float | Runtime cap for the chunk. |
| `enumeration.progress_every` | integer | Progress print interval. |
| `enumeration.max_match_examples` | integer | Maximum examples stored. |
| `enumeration.store_signature_counts` | bool | Store raw signature counts. |
| `enumeration.store_orbit_signature_counts` | bool | Store orbit-class signature counts. |
| `orbit_reduction.enabled` | bool | Request orbit canonicalization. |
| `orbit_reduction.max_automorphisms` | integer | Cap for automorphism enumeration. |
| `orbit_reduction.timeout_seconds_soft` | integer/float | Soft timeout for automorphism enumeration. |
| `orbit_reduction.require_networkx_for_orbit_reduction` | bool | If true, fail when networkx is unavailable. |
| `role_assignment.mode` | string | Role assignment mode; v0 supports type-preferred. |
| `near_signature.max_abs_difference_sum` | integer | Near-signature distance threshold. |

---

## 3. Reference signature JSON

Output:

```text
bms_fu02g4c_reference_patch_signature.json
```

| field name | type | description |
|---|---:|---|
| `carrier_set` | list[string] | Reference carrier faces. |
| `mixed_core_set` | list[string] | Reference mixed-core faces. |
| `pentagon_boundary_set` | list[string] | Reference pentagon-boundary faces. |
| `reference_is_connected` | bool | Whether reference carrier set is connected. |
| `carrier_face_count` | integer | Number of carrier faces. |
| `carrier_hexagon_count` | integer | Number of hexagon carrier faces. |
| `carrier_pentagon_count` | integer | Number of pentagon carrier faces. |
| `carrier_component_count` | integer | Connected component count. |
| `largest_carrier_component_count` | integer | Largest component size. |
| `carrier_internal_adjacency_count` | integer | Internal carrier adjacencies. |
| `carrier_boundary_adjacency_count` | integer | Carrier/noncarrier boundary adjacencies. |
| `carrier_external_neighbor_count` | integer | Distinct external neighbor count. |
| `carrier_induced_degree_histogram` | object | Induced degree histogram. |
| `boundary_neighbor_type_counts` | object | External boundary neighbor type counts. |
| `mixed_core_count` | integer | Mixed-core role count. |
| `pentagon_boundary_count` | integer | Pentagon-boundary role count. |
| `mixed_core_internal_adjacency_count` | integer | Internal mixed-core adjacencies. |
| `pentagon_boundary_internal_adjacency_count` | integer | Internal boundary-role adjacencies. |
| `mixed_to_pentagon_boundary_adjacency_count` | integer | Cross-role adjacencies. |
| `mixed_core_induced_degree_histogram` | object | Mixed-core induced degree histogram. |
| `pentagon_boundary_induced_degree_histogram` | object | Boundary-role induced degree histogram. |
| `carrier_signature_string` | string | Stable uncolored signature string. |
| `role_colored_signature_string` | string | Stable role-colored signature string. |

---

## 4. Chunk summary JSON

Output:

```text
bms_fu02g4c_chunk_summary.json
```

| field name | type | description |
|---|---:|---|
| `chunk_id` | string | Chunk identifier. |
| `enumeration_status` | string | `complete`, `partial_chunk_limit_reached`, `partial_timeout_reached`, or `partial_runtime_error`. |
| `elapsed_seconds` | float | Runtime. |
| `target_patch_size` | integer | Patch size. |
| `reference_is_connected` | bool | Reference connectivity guard. |
| `skip_first_raw_patches` | integer | Raw patches skipped. |
| `raw_patch_count_seen_including_skipped` | integer | Raw emitted patches seen including skipped range. |
| `raw_patch_count_skipped` | integer | Number of skipped raw patches. |
| `raw_connected_patch_count_processed` | integer | Raw patches processed in this chunk. |
| `raw_carrier_signature_exact_match_count` | integer | Raw exact uncolored matches. |
| `raw_carrier_signature_exact_match_fraction` | float | Raw exact uncolored match fraction. |
| `raw_carrier_signature_near_match_count` | integer | Raw near uncolored matches. |
| `raw_carrier_signature_near_match_fraction` | float | Raw near uncolored match fraction. |
| `raw_role_colored_signature_exact_match_count` | integer | Raw exact role-colored matches. |
| `raw_role_colored_signature_exact_match_fraction` | float | Raw exact role-colored match fraction. |
| `raw_role_colored_signature_near_match_count` | integer | Raw near role-colored matches. |
| `raw_role_colored_signature_near_match_fraction` | float | Raw near role-colored match fraction. |
| `near_signature_max_abs_difference_sum` | integer | Near threshold. |
| `orbit_reduction_enabled_actual` | bool | Whether orbit reduction actually ran. |
| `automorphism_count_used` | integer | Number of automorphisms used. |
| `unique_orbit_patch_count_processed` | integer/null | Unique canonical patch classes processed. |
| `orbit_carrier_signature_exact_match_class_count` | integer/null | Orbit-class exact uncolored matches. |
| `orbit_carrier_signature_near_match_class_count` | integer/null | Orbit-class near uncolored matches. |
| `orbit_role_colored_signature_exact_match_class_count` | integer/null | Orbit-class exact role-colored matches. |
| `orbit_role_colored_signature_near_match_class_count` | integer/null | Orbit-class near role-colored matches. |
| `unique_raw_carrier_signature_count` | integer/string | Unique raw uncolored signatures. |
| `unique_raw_role_colored_signature_count` | integer/string | Unique raw role-colored signatures. |
| `unique_orbit_carrier_signature_count` | integer/string | Unique orbit-class uncolored signatures. |
| `unique_orbit_role_colored_signature_count` | integer/string | Unique orbit-class role-colored signatures. |
| `scope_note` | string | Chunk/exhaustiveness caveat. |
| `role_assignment_note` | string | Role assignment caveat. |

---

## 5. Orbit reduction summary

Output:

```text
bms_fu02g4c_orbit_reduction_summary.json
```

| field name | type | description |
|---|---:|---|
| `orbit_reduction_requested` | bool | Whether config requested orbit reduction. |
| `orbit_reduction_enabled_actual` | bool | Whether orbit reduction actually ran. |
| `automorphism_count_used` | integer | Number of automorphisms used. |
| `scope_note` | string | Canonicalization description. |

---

## 6. Match examples CSV

Outputs:

```text
bms_fu02g4c_match_examples.csv
bms_fu02g4c_orbit_match_examples.csv
```

| field name | type | description |
|---|---:|---|
| `scope` | string | `raw` or `orbit_class`. |
| `match_type` | string | `carrier_exact`, `carrier_near`, `role_exact`, or `role_near`. |
| `patch_faces` | string | Semicolon-separated raw patch faces. |
| `canonical_patch_faces` | string | Semicolon-separated canonical patch faces if orbit-reduced. |
| `signature_distance` | integer | Uncolored signature distance. |
| `role_signature_distance` | integer | Role-colored signature distance. |
| `carrier_hexagon_count` | integer | Carrier hexagon count. |
| `carrier_pentagon_count` | integer | Carrier pentagon count. |
| `carrier_internal_adjacency_count` | integer | Internal adjacency count. |
| `carrier_boundary_adjacency_count` | integer | Boundary adjacency count. |
| `carrier_external_neighbor_count` | integer | External neighbor count. |

---

## 7. Signature counts CSV

Optional output:

```text
bms_fu02g4c_signature_counts.csv
```

| field name | type | description |
|---|---:|---|
| `scope` | string | `raw` or `orbit_class`. |
| `signature_kind` | string | `carrier` or `role_colored`. |
| `signature_string` | string | Signature string. |
| `count` | integer | Frequency. |

---

## 8. Manifest

Output:

```text
bms_fu02g4c_run_manifest.json
```

| field name | type | description |
|---|---:|---|
| `run_id` | string | Run id. |
| `chunk_id` | string | Chunk id. |
| `output_dir` | string | Output directory. |
| `enumeration_status` | string | Chunk status. |
| `target_patch_size` | integer | Patch size. |
| `reference_is_connected` | bool | Reference connectivity. |
| `skip_first_raw_patches` | integer | Skipped patch count. |
| `raw_connected_patch_count_processed` | integer | Processed patch count. |
| `raw_patch_count_seen_including_skipped` | integer | Seen including skip. |
| `orbit_reduction_enabled_actual` | bool | Actual orbit reduction status. |
| `unique_orbit_patch_count_processed` | integer/null | Unique orbit classes. |
| `warnings_count` | integer | Warning count. |
| `scope_note` | string | Chunk/exhaustiveness caveat. |

---

## 9. Interpretation boundary

A single g4c run is a chunk unless:

```text
enumeration_status = complete
```

and previous skipped ranges are known to be covered.

Use:

```text
chunk evidence
bounded resumable enumeration
orbit-canonical class count
```

Do not use:

```text
exhaustive
```

until all chunks cover the full enumeration.
