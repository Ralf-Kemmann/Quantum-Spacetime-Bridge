# BMS-FU02g4b — Exhaustive Connected Patch Signature Check Field List

Date: 2026-05-03  
Project: Gravitation und RaumZeit / Quantum-Spacetime-Bridge  
Recommended repo target: `docs/BMS_FU02G4B_EXHAUSTIVE_CONNECTED_PATCH_SIGNATURE_CHECK_FIELD_LIST.md`  
Status: Companion field list for BMS-FU02g4b

---

## 1. Purpose

BMS-FU02g4b enumerates connected same-size C60 face patches and counts exact or
near matches to the FU02f1 reference patch signatures.

The central trust field is:

```text
enumeration_status
```

Only `complete` supports exhaustive wording.

---

## 2. Config fields

| field name | type | description |
|---|---:|---|
| `run.run_id` | string | Stable run identifier. |
| `run.output_dir` | string | Output directory. |
| `run.random_seed` | integer | Reserved seed; enumeration itself is deterministic. |
| `inputs.c60_cells_csv` | string | C60 cell table. |
| `inputs.c60_edges_csv` | string | C60 edge table with incident cell fields. |
| `inputs.fu02f1_face_layout_csv` | string | FU02f1 face-role reference. |
| `inputs.fu02g4_reference_signature_json` | string | Optional FU02g4 reference signature. |
| `reference_roles.mixed_core_role` | string | FU02f1 label mapped to mixed core. |
| `reference_roles.pentagon_boundary_role` | string | FU02f1 label mapped to pentagon boundary. |
| `reference_roles.adjacent_shell_role` | string | FU02f1 adjacent shell label. |
| `reference_roles.noncarrier_role` | string | FU02f1 noncarrier label. |
| `enumeration.target_patch_size` | integer/string | Patch size or `reference`. |
| `enumeration.max_patches` | integer | Maximum emitted connected patches before partial stop. |
| `enumeration.timeout_seconds` | integer/float | Runtime cap. |
| `enumeration.progress_every` | integer | Progress print interval. |
| `enumeration.store_patch_signature_counts` | bool | Store signature frequency counts. |
| `enumeration.max_match_examples` | integer | Maximum match/near-match examples stored. |
| `role_assignment.mode` | string | Candidate role assignment mode. |
| `near_signature.max_abs_difference_sum` | integer | Near-signature threshold. |

---

## 3. Reference patch signature JSON

Output:

```text
bms_fu02g4b_reference_patch_signature.json
```

| field name | type | description |
|---|---:|---|
| `carrier_set` | list[string] | Reference carrier faces. |
| `mixed_core_set` | list[string] | Reference mixed-core faces. |
| `pentagon_boundary_set` | list[string] | Reference pentagon-boundary faces. |
| `carrier_face_count` | integer | Carrier count. |
| `carrier_hexagon_count` | integer | Carrier hexagon count. |
| `carrier_pentagon_count` | integer | Carrier pentagon count. |
| `carrier_component_count` | integer | Carrier component count. |
| `largest_carrier_component_count` | integer | Largest component size. |
| `carrier_internal_adjacency_count` | integer | Internal carrier adjacencies. |
| `carrier_boundary_adjacency_count` | integer | Carrier/noncarrier boundary adjacencies. |
| `carrier_external_neighbor_count` | integer | External neighbor count. |
| `carrier_induced_degree_histogram` | object | Carrier induced degree histogram. |
| `boundary_neighbor_type_counts` | object | External neighbor type counts. |
| `mixed_core_count` | integer | Mixed-core role count. |
| `pentagon_boundary_count` | integer | Pentagon-boundary role count. |
| `mixed_core_internal_adjacency_count` | integer | Mixed-core internal adjacencies. |
| `pentagon_boundary_internal_adjacency_count` | integer | Boundary-role internal adjacencies. |
| `mixed_to_pentagon_boundary_adjacency_count` | integer | Cross-role adjacencies. |
| `mixed_core_induced_degree_histogram` | object | Mixed-core induced degree histogram. |
| `pentagon_boundary_induced_degree_histogram` | object | Boundary-role induced degree histogram. |
| `carrier_signature_string` | string | Stable uncolored signature. |
| `role_colored_signature_string` | string | Stable role-colored signature. |

---

## 4. Enumeration summary JSON

Output:

```text
bms_fu02g4b_enumeration_summary.json
```

| field name | type | description |
|---|---:|---|
| `enumeration_status` | string | `complete` or partial status. |
| `elapsed_seconds` | float | Runtime. |
| `target_patch_size` | integer | Patch size. |
| `enumerated_connected_patch_count` | integer | Number of emitted connected patches. |
| `carrier_signature_exact_match_count` | integer | Exact uncolored match count. |
| `carrier_signature_exact_match_fraction` | float | Exact uncolored match fraction. |
| `carrier_signature_near_match_count` | integer | Near uncolored match count. |
| `carrier_signature_near_match_fraction` | float | Near uncolored match fraction. |
| `role_colored_signature_exact_match_count` | integer | Exact role-colored match count. |
| `role_colored_signature_exact_match_fraction` | float | Exact role-colored match fraction. |
| `role_colored_signature_near_match_count` | integer | Near role-colored match count. |
| `role_colored_signature_near_match_fraction` | float | Near role-colored match fraction. |
| `near_signature_max_abs_difference_sum` | integer | Near-signature threshold. |
| `unique_carrier_signature_count` | integer/string | Unique uncolored signature count if stored. |
| `unique_role_colored_signature_count` | integer/string | Unique role-colored signature count if stored. |
| `diagnostic_label` | string | Summary label. |
| `scope_note` | string | Exhaustiveness caveat. |

---

## 5. Match examples CSV

Output:

```text
bms_fu02g4b_match_examples.csv
```

| field name | type | description |
|---|---:|---|
| `match_type` | string | `carrier_exact`, `carrier_near`, `role_exact`, or `role_near`. |
| `patch_faces` | string | Semicolon-separated patch faces. |
| `carrier_signature_string` | string | Candidate uncolored signature. |
| `role_colored_signature_string` | string | Candidate role-colored signature. |
| `signature_distance` | integer | Uncolored distance to reference. |
| `role_signature_distance` | integer | Role-colored distance to reference. |
| `carrier_hexagon_count` | integer | Candidate hexagon count. |
| `carrier_pentagon_count` | integer | Candidate pentagon count. |
| `carrier_internal_adjacency_count` | integer | Candidate internal carrier adjacency count. |
| `carrier_boundary_adjacency_count` | integer | Candidate boundary adjacency count. |
| `carrier_external_neighbor_count` | integer | Candidate external neighbor count. |

---

## 6. Signature count summary JSON

Output:

```text
bms_fu02g4b_signature_count_summary.json
```

| field name | type | description |
|---|---:|---|
| `store_patch_signature_counts` | bool | Whether counts were stored. |
| `unique_carrier_signature_count` | integer/null | Unique uncolored signature count. |
| `unique_role_colored_signature_count` | integer/null | Unique role-colored signature count. |
| `top_carrier_signatures` | list | Most frequent uncolored signatures. |
| `top_role_colored_signatures` | list | Most frequent role-colored signatures. |

---

## 7. Patch signature counts CSV

Optional output:

```text
bms_fu02g4b_patch_signature_counts.csv
```

| field name | type | description |
|---|---:|---|
| `signature_kind` | string | `carrier` or `role_colored`. |
| `signature_string` | string | Signature string. |
| `count` | integer | Frequency. |

---

## 8. Run manifest

Output:

```text
bms_fu02g4b_run_manifest.json
```

| field name | type | description |
|---|---:|---|
| `run_id` | string | Run id. |
| `output_dir` | string | Output directory. |
| `enumeration_status` | string | Exhaustiveness status. |
| `target_patch_size` | integer | Patch size. |
| `enumerated_connected_patch_count` | integer | Number of enumerated patches. |
| `warnings_count` | integer | Warning count. |
| `scope_note` | string | Scope caveat. |

---

## 9. Interpretation boundary

Allowed if complete:

```text
The connected same-size patch enumeration completed under the specified graph
and deterministic role assignment.
```

Allowed if partial:

```text
The run provides bounded enumeration evidence up to the stated cap/timeout.
```

Not allowed:

```text
No universal real-structure-memory proof, spacetime proof, or chemistry claim.
```
