# BMS-FU02e — Runner Field List

Date: 2026-05-02  
Project: Gravitation und RaumZeit / Quantum-Spacetime-Bridge  
Recommended repo target: `docs/BMS_FU02E_RUNNER_FIELD_LIST.md`  
Status: Companion field list for BMS-FU02e carrier role null localization test

---

## 1. Purpose

BMS-FU02e tests whether the FU02d1 connected 17-face carrier region is reproduced by role-assignment null families on the fixed validated C60 graph.

Core question:

```text
Ist diese Face-Landschaft spezifisch oder billig nachbaubar?
```

---

## 2. Config fields

| field name | type | description |
|---|---:|---|
| `run.run_id` | string | Stable run identifier. |
| `run.output_dir` | string | Output directory. |
| `run.random_seed` | integer | Random seed for null generation. |
| `run.repeats_per_null_family` | integer | Number of replicates per null family. |
| `inputs.fu02d1_output_dir` | string | FU02d1 output directory. |
| `inputs.fu02d_output_dir` | string | FU02d output directory. |
| `inputs.c60_edges_csv` | string | Validated C60 edge table. |
| `inputs.c60_nodes_csv` | string | Validated C60 node table. |
| `inputs.c60_faces_csv` | string | Validated C60 face table. |
| `inputs.c60_graph_manifest_json` | string | C60 validation manifest. |
| `null_families.include` | list[string] | Null families to run. |
| `real_roles.hh_consensus_role_group` | string | FU02d role group for H,H consensus edges. |
| `real_roles.hp_secondary_role_group` | string | FU02d role group for H,P secondary edges. |

---

## 3. Null families

| null family | type | description |
|---|---:|---|
| `edge_type_preserving_role_shuffle` | role-assignment null | Shuffles H,H labels among H,H edges and H,P labels among H,P edges. |
| `degree_spread_role_shuffle` | role-assignment null | Explicit degree-spread family; for 3-regular C60 mostly equals edge-type preserving shuffle. |
| `component_size_preserving_hp_shuffle` | role-assignment null | Preserves H,P component size multiset approximately using connected H,P subsets. |
| `hh_anchor_neighborhood_decoy` | role-aware decoy | Places H,P carriers preferentially near shuffled H,H anchors. |

---

## 4. Null localization metrics

Output:

```text
bms_fu02e_null_localization_metrics.csv
```

| field name | type | description |
|---|---:|---|
| `null_family` | string | Null family id. |
| `replicate_index` | integer | Replicate index. |
| `hh_edge_count` | integer | Number of H,H carrier edges assigned. |
| `hp_edge_count` | integer | Number of H,P carrier edges assigned. |
| `carrier_face_count` | integer | Number of faces incident to any carrier edge. |
| `carrier_face_fraction` | float | Fraction of faces incident to any carrier edge. |
| `carrier_face_component_count` | integer | Number of connected components among carrier faces. |
| `largest_carrier_face_component_count` | integer | Largest carrier-face component size. |
| `hh_face_count` | integer | Number of faces incident to H,H carrier edges. |
| `hp_face_count` | integer | Number of faces incident to H,P carrier edges. |
| `mixed_seam_boundary_face_count` | integer | Faces incident to both H,H and H,P carrier edges. |
| `hp_boundary_face_count` | integer | Faces incident only to H,P carrier edges. |
| `carrier_adjacent_face_count` | integer | Noncarrier faces adjacent to carrier faces. |
| `noncarrier_face_count` | integer | Faces neither carrier nor adjacent. |
| `carrier_hexagon_face_count` | integer | Carrier faces of type H. |
| `carrier_pentagon_face_count` | integer | Carrier faces of type P. |
| `mixed_face_hexagon_count` | integer | Mixed faces of type H. |
| `mixed_face_pentagon_count` | integer | Mixed faces of type P. |
| `hh_face_component_count` | integer | Component count of H,H faces. |
| `largest_hh_face_component_count` | integer | Largest H,H face component. |
| `hp_face_component_count` | integer | Component count of H,P faces. |
| `largest_hp_face_component_count` | integer | Largest H,P face component. |
| `mixed_face_component_count` | integer | Component count of mixed faces. |
| `largest_mixed_face_component_count` | integer | Largest mixed-face component. |

---

## 5. Real vs null summary

Output:

```text
bms_fu02e_real_vs_null_summary.csv
```

| field name | type | description |
|---|---:|---|
| `null_family` | string | Null family id. |
| `metric_name` | string | Compared metric. |
| `real_value` | float | Real FU02d1 metric value. |
| `null_mean` | float | Null mean. |
| `null_std` | float | Null population standard deviation. |
| `null_min` | float | Null minimum. |
| `null_median` | float | Null median. |
| `null_max` | float | Null maximum. |
| `null_replicate_count` | integer | Number of null replicates. |
| `empirical_ge_fraction` | float | Fraction of nulls with value greater than or equal to real. |
| `empirical_le_fraction` | float | Fraction of nulls with value less than or equal to real. |
| `rank_position_of_real` | integer | Rank of real if inserted into descending null distribution. |
| `interpretation_label` | string | Diagnostic interpretation label. |

Interpretation labels:

```text
real_high_relative_to_null
real_low_relative_to_null
null_reproduces_metric_behavior
mixed_or_metric_dependent
```

---

## 6. Null family inventory

Output:

```text
bms_fu02e_null_family_inventory.csv
```

| field name | type | description |
|---|---:|---|
| `null_family` | string | Null family id. |
| `replicate_count` | integer | Number of replicates. |
| `hh_edge_count_per_replicate` | integer | H,H carrier count per replicate. |
| `hp_edge_count_per_replicate` | integer | H,P carrier count per replicate. |
| `description` | string | Human-readable null-family description. |

---

## 7. Real face metrics

Output:

```text
bms_fu02e_real_face_metrics.json
```

JSON object containing the FU02d1 real metrics recomputed by FU02e.

---

## 8. Null assignment sample

Output:

```text
bms_fu02e_null_carrier_assignments_sample.csv
```

| field name | type | description |
|---|---:|---|
| `null_family` | string | Null family id. |
| `replicate_index` | integer | Replicate index. |
| `hh_edges` | string | Assigned H,H carrier edges. |
| `hp_edges` | string | Assigned H,P carrier edges. |
| `carrier_face_ids` | string | Carrier faces in this replicate. |
| `mixed_face_ids` | string | Mixed faces in this replicate. |

---

## 9. Interpretation boundary

Allowed:

```text
FU02e compares the real FU02d1 face-localization pattern against role-assignment
null families on the fixed C60 graph.
```

Not allowed:

```text
FU02e computes formal physical p-values or proves physical spacetime.
```
