# BMS-FU02g3 — Real-Structure Memory Null Specificity Field List

Date: 2026-05-02  
Project: Gravitation und RaumZeit / Quantum-Spacetime-Bridge  
Recommended repo target: `docs/BMS_FU02G3_REAL_STRUCTURE_MEMORY_NULL_SPECIFICITY_FIELD_LIST.md`  
Status: Companion field list for BMS-FU02g3

---

## 1. Purpose

BMS-FU02g3 tests whether the FU02f1 C60 role-colored carrier region is cheap or
rare under selected same-C60 face-graph null patch families.

No universal p-values or final physics claims are made.

---

## 2. Config fields

| field name | type | description |
|---|---:|---|
| `run.run_id` | string | Stable run identifier. |
| `run.output_dir` | string | Output directory. |
| `run.random_seed` | integer | Deterministic random seed. |
| `inputs.c60_cells_csv` | string | C60 cell table. |
| `inputs.c60_edges_csv` | string | C60 edge table. |
| `inputs.c60_nodes_csv` | string | C60 node table. |
| `inputs.fu02f1_face_layout_csv` | string | FU02f1 C60 face-role reference. |
| `inputs.fu02g2_cell_diagnostics_csv` | string | Optional FU02g2 generic proxy diagnostics. |
| `reference_roles.carrier_roles` | list[string] | FU02f1 labels treated as carrier roles. |
| `reference_roles.mixed_core_role` | string | FU02f1 label mapped to mixed core. |
| `reference_roles.pentagon_boundary_role` | string | FU02f1 label mapped to pentagon boundary. |
| `reference_roles.adjacent_shell_role` | string | FU02f1 label mapped to adjacent shell. |
| `reference_roles.noncarrier_role` | string | FU02f1 label mapped to noncarrier. |
| `nulls.repeats_per_family` | integer | Number of repeats per null family. |
| `nulls.families.<family>.enabled` | bool | Enables a null family. |
| `near_reference.carrier_overlap_fraction_min` | float | Minimum carrier-overlap fraction for near-reference. |
| `near_reference.role_balance_deviation_max` | integer | Maximum role-balance deviation. |
| `near_reference.require_connected` | bool | Require one carrier component. |
| `near_reference.compactness_min` | float | Minimum compactness proxy. |
| `strict_near_reference.*` | mixed | Strict version of near-reference criteria. |

---

## 3. Reference profile JSON

Output:

```text
bms_fu02g3_reference_profile.json
```

| field name | type | description |
|---|---:|---|
| `carrier_set` | list[string] | FU02f1 reference carrier faces. |
| `mixed_core_set` | list[string] | FU02f1 mixed-core faces. |
| `pentagon_boundary_set` | list[string] | FU02f1 pentagon-boundary faces. |
| `adjacent_shell_set` | list[string] | FU02f1 adjacent-shell faces. |
| `noncarrier_set` | list[string] | FU02f1 noncarrier faces. |
| `carrier_face_count` | integer | Number of reference carrier faces. |
| `mixed_core_count` | integer | Number of mixed-core faces. |
| `pentagon_boundary_count` | integer | Number of pentagon-boundary faces. |
| `carrier_hexagon_count` | integer | Reference carrier hexagon count. |
| `carrier_pentagon_count` | integer | Reference carrier pentagon count. |
| `carrier_component_count` | integer | Components in reference carrier set. |
| `largest_carrier_component_count` | integer | Largest component size. |
| `compactness_proxy` | float | Largest component / carrier count. |
| `carrier_internal_adjacency_count` | integer | Internal carrier adjacencies. |
| `carrier_boundary_adjacency_count` | integer | Carrier/noncarrier adjacencies. |
| `carrier_external_neighbor_count` | integer | External neighbor count. |
| `role_mapping_note` | string | Role-mapping caveat. |

---

## 4. Null replicates CSV

Output:

```text
bms_fu02g3_null_replicates.csv
```

| field name | type | description |
|---|---:|---|
| `null_family` | string | Null family label. |
| `replicate_id` | integer | Replicate id. |
| `carrier_face_count` | integer | Carrier face count. |
| `mixed_core_count` | integer | Assigned mixed-core count. |
| `pentagon_boundary_count` | integer | Assigned pentagon-boundary count. |
| `carrier_hexagon_count` | integer | Carrier hexagon count. |
| `carrier_pentagon_count` | integer | Carrier pentagon count. |
| `carrier_overlap_count` | integer | Overlap with reference carrier set. |
| `carrier_overlap_fraction` | float | Overlap / reference carrier count. |
| `mixed_core_overlap_count` | integer | Mixed-core overlap with reference. |
| `mixed_core_overlap_fraction` | float | Mixed overlap / reference mixed count. |
| `pentagon_boundary_overlap_count` | integer | Pentagon-boundary overlap. |
| `pentagon_boundary_overlap_fraction` | float | Pentagon-boundary overlap fraction. |
| `role_balance_deviation` | integer | Deviation from reference role/type counts. |
| `carrier_component_count` | integer | Number of carrier components. |
| `largest_carrier_component_count` | integer | Largest carrier component size. |
| `compactness_proxy` | float | Largest carrier component / carrier count. |
| `carrier_internal_adjacency_count` | integer | Internal carrier adjacencies. |
| `carrier_boundary_adjacency_count` | integer | Carrier boundary adjacencies. |
| `carrier_external_neighbor_count` | integer | Distinct external neighbors. |
| `near_reference` | integer | 1 if near-reference criteria met. |
| `strict_near_reference` | integer | 1 if strict criteria met. |

---

## 5. Null family summary CSV

Output:

```text
bms_fu02g3_null_family_summary.csv
```

| field name | type | description |
|---|---:|---|
| `null_family` | string | Null family. |
| `replicate_count` | integer | Number of replicates. |
| `near_reference_count` | integer | Near-reference replicate count. |
| `near_reference_fraction` | float | Near-reference replicate fraction. |
| `strict_near_reference_count` | integer | Strict near-reference count. |
| `strict_near_reference_fraction` | float | Strict near-reference fraction. |
| `median_carrier_overlap_fraction` | float | Median carrier overlap fraction. |
| `max_carrier_overlap_fraction` | float | Max carrier overlap fraction. |
| `min_role_balance_deviation` | float | Minimum role-balance deviation. |
| `median_role_balance_deviation` | float | Median role-balance deviation. |
| `median_compactness_proxy` | float | Median compactness. |
| `max_compactness_proxy` | float | Max compactness. |
| `diagnostic_label` | string | Family-level interpretation label. |

---

## 6. Generic proxy overlap CSV

Output:

```text
bms_fu02g3_generic_proxy_reference_overlap.csv
```

| field name | type | description |
|---|---:|---|
| `structure_id` | string | Structure id. |
| `carrier_count` | integer | Generic proxy carrier count. |
| `carrier_overlap_count` | integer | Generic proxy overlap with FU02f1 reference carrier set. |
| `carrier_overlap_fraction` | float | Generic proxy overlap fraction. |
| `mixed_core_overlap_count` | integer | Generic proxy overlap with mixed core. |
| `pentagon_boundary_overlap_count` | integer | Generic proxy overlap with pentagon boundary. |
| `role_balance_deviation` | string/integer | Not applicable for generic proxy roles in v0. |
| `note` | string | Explanation. |

---

## 7. Interpretation boundary

Allowed:

```text
FU02g3 tests FU02f1 role-colored C60 carrier-region cheapness under selected
same-C60 null patch families.
```

Not allowed:

```text
FU02g3 proves final real-structure memory, physical symmetry recovery,
chemistry, spacetime or universal significance.
```
