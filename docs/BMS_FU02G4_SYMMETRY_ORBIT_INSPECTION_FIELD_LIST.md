# BMS-FU02g4 — Symmetry-Orbit Inspection Field List

Date: 2026-05-03  
Project: Gravitation und RaumZeit / Quantum-Spacetime-Bridge  
Recommended repo target: `docs/BMS_FU02G4_SYMMETRY_ORBIT_INSPECTION_FIELD_LIST.md`  
Status: Companion field list for BMS-FU02g4

---

## 1. Purpose

BMS-FU02g4 inspects whether the FU02f1 C60 reference carrier region is merely a
common connected patch or a more constrained role-colored symmetry/signature
class.

No physical spacetime or chemistry claim is made.

---

## 2. Config fields

| field name | type | description |
|---|---:|---|
| `run.run_id` | string | Stable run identifier. |
| `run.output_dir` | string | Output directory. |
| `run.random_seed` | integer | Random seed for connected patch sampling. |
| `inputs.c60_cells_csv` | string | C60 cell table. |
| `inputs.c60_edges_csv` | string | C60 edge table with incident cells. |
| `inputs.fu02f1_face_layout_csv` | string | FU02f1 face-role reference table. |
| `inputs.fu02g3_reference_profile_json` | string | Optional FU02g3 reference profile. |
| `reference_roles.mixed_core_role` | string | FU02f1 label mapped to mixed core. |
| `reference_roles.pentagon_boundary_role` | string | FU02f1 label mapped to pentagon boundary. |
| `reference_roles.adjacent_shell_role` | string | FU02f1 adjacent shell label. |
| `reference_roles.noncarrier_role` | string | FU02f1 noncarrier label. |
| `automorphism.enabled` | bool | Enables automorphism enumeration if networkx is available. |
| `automorphism.max_automorphisms` | integer | Hard cap for enumerated automorphisms. |
| `automorphism.timeout_seconds_soft` | integer/float | Soft timeout for enumeration. |
| `connected_patch_sampling.enabled` | bool | Enables connected same-size patch sampling. |
| `connected_patch_sampling.sample_count` | integer | Number of sampled patches. |
| `connected_patch_sampling.exact_size` | bool | Require same carrier set size. |
| `near_signature.max_abs_difference_sum` | integer | Near-signature threshold over selected count features. |

---

## 3. Reference patch signature JSON

Output:

```text
bms_fu02g4_reference_patch_signature.json
```

| field name | type | description |
|---|---:|---|
| `carrier_set` | list[string] | Reference carrier faces. |
| `mixed_core_set` | list[string] | Reference mixed-core faces. |
| `pentagon_boundary_set` | list[string] | Reference pentagon-boundary faces. |
| `carrier_face_count` | integer | Carrier set size. |
| `carrier_hexagon_count` | integer | Carrier hexagon count. |
| `carrier_pentagon_count` | integer | Carrier pentagon count. |
| `carrier_component_count` | integer | Carrier connected-component count. |
| `largest_carrier_component_count` | integer | Largest carrier component size. |
| `carrier_internal_adjacency_count` | integer | Internal carrier adjacencies. |
| `carrier_boundary_adjacency_count` | integer | Carrier/noncarrier adjacencies. |
| `carrier_external_neighbor_count` | integer | External neighbor count. |
| `carrier_induced_degree_histogram` | object | Induced degree histogram of carrier patch. |
| `boundary_neighbor_type_counts` | object | External neighbor cell-type counts. |
| `mixed_core_count` | integer | Mixed-core face count. |
| `pentagon_boundary_count` | integer | Pentagon-boundary role count. |
| `mixed_core_internal_adjacency_count` | integer | Internal adjacencies among mixed-core faces. |
| `pentagon_boundary_internal_adjacency_count` | integer | Internal adjacencies among pentagon-boundary role faces. |
| `mixed_to_pentagon_boundary_adjacency_count` | integer | Cross-role adjacencies. |
| `mixed_core_induced_degree_histogram` | object | Mixed-core induced degree histogram. |
| `pentagon_boundary_induced_degree_histogram` | object | Boundary-role induced degree histogram. |
| `carrier_signature_string` | string | Stable uncolored patch signature string. |
| `role_colored_signature_string` | string | Stable role-colored patch signature string. |

---

## 4. Automorphism orbit summary JSON

Output:

```text
bms_fu02g4_automorphism_orbit_summary.json
```

| field name | type | description |
|---|---:|---|
| `enabled` | bool | Whether automorphism enumeration was requested. |
| `status` | string | `complete`, `partial`, `disabled`, or skipped status. |
| `stopped_reason` | string | Stop reason for enumeration. |
| `automorphism_count_observed` | integer | Observed automorphism count. |
| `carrier_orbit_size_observed` | integer | Number of distinct carrier-set images. |
| `role_colored_orbit_size_observed` | integer | Number of distinct role-colored images. |
| `carrier_stabilizer_size_observed` | integer | Automorphisms preserving carrier set exactly. |
| `role_colored_stabilizer_size_observed` | integer | Automorphisms preserving role-colored assignment exactly. |
| `node_match_preserves_cell_type` | bool | Whether face type was preserved. |
| `scope_note` | string | Scope caveat. |

---

## 5. Connected patch signature samples CSV

Output:

```text
bms_fu02g4_connected_patch_signature_samples.csv
```

| field name | type | description |
|---|---:|---|
| `sample_id` | integer | Sample id. |
| `carrier_faces` | string | Semicolon-separated sampled carrier faces. |
| `carrier_signature_string` | string | Uncolored signature string. |
| `role_colored_signature_string` | string | Role-colored signature string. |
| `carrier_signature_match` | integer | 1 if uncolored signature matches reference. |
| `role_colored_signature_match` | integer | 1 if role-colored signature matches reference. |
| `near_carrier_signature` | integer | 1 if uncolored signature is near reference. |
| `near_role_colored_signature` | integer | 1 if role-colored signature is near reference. |
| `carrier_hexagon_count` | integer | Sample carrier hexagon count. |
| `carrier_pentagon_count` | integer | Sample carrier pentagon count. |
| `carrier_component_count` | integer | Sample carrier component count. |
| `largest_carrier_component_count` | integer | Largest component size. |
| `carrier_internal_adjacency_count` | integer | Internal carrier adjacencies. |
| `carrier_boundary_adjacency_count` | integer | Boundary adjacencies. |
| `carrier_external_neighbor_count` | integer | External neighbor count. |

---

## 6. Signature match summary JSON

Output:

```text
bms_fu02g4_signature_match_summary.json
```

| field name | type | description |
|---|---:|---|
| `sample_count` | integer | Number of sampled connected patches. |
| `carrier_signature_match_count` | integer | Exact uncolored signature match count. |
| `carrier_signature_match_fraction` | float | Exact uncolored match fraction. |
| `role_colored_signature_match_count` | integer | Exact role-colored signature match count. |
| `role_colored_signature_match_fraction` | float | Exact role-colored match fraction. |
| `near_carrier_signature_count` | integer | Near uncolored signature count. |
| `near_carrier_signature_fraction` | float | Near uncolored signature fraction. |
| `near_role_colored_signature_count` | integer | Near role-colored signature count. |
| `near_role_colored_signature_fraction` | float | Near role-colored signature fraction. |
| `near_signature_max_abs_difference_sum` | integer | Near-signature threshold. |
| `diagnostic_label` | string | Match interpretation label. |
| `scope_note` | string | Sampling caveat. |

---

## 7. Run manifest

Output:

```text
bms_fu02g4_run_manifest.json
```

| field name | type | description |
|---|---:|---|
| `run_id` | string | Run id. |
| `output_dir` | string | Output directory. |
| `reference_carrier_face_count` | integer | Reference carrier count. |
| `reference_mixed_core_count` | integer | Mixed-core count. |
| `reference_pentagon_boundary_count` | integer | Pentagon-boundary role count. |
| `automorphism_status` | string | Automorphism summary status. |
| `connected_patch_sample_count` | integer | Sample count. |
| `warnings_count` | integer | Warning count. |
| `scope_note` | string | Scope caveat. |

---

## 8. Interpretation boundary

Allowed:

```text
FU02g4 reports graph/symmetry orbit and patch-signature diagnostics for the
FU02f1 C60 reference carrier region.
```

Not allowed:

```text
FU02g4 proves physical real-structure memory, molecular chemistry, spacetime,
or uniqueness beyond the tested graph/signature scope.
```
