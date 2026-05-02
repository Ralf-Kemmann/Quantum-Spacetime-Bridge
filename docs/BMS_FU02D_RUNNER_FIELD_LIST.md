# BMS-FU02d — Runner Field List

Date: 2026-05-02  
Project: Gravitation und RaumZeit / Quantum-Spacetime-Bridge  
Recommended repo target: `docs/BMS_FU02D_RUNNER_FIELD_LIST.md`  
Status: Companion field list for BMS-FU02d carrier role geometry and patch distribution

---

## 1. Purpose

BMS-FU02d maps FU02c carrier roles on the validated C60 cage graph.

Core question:

```text
Wo sitzen H,H consensus carriers and H,P secondary carriers im Käfig?
```

---

## 2. Config fields

| field name | type | description |
|---|---:|---|
| `run.run_id` | string | Stable run identifier. |
| `run.output_dir` | string | Output directory. |
| `inputs.fu02c_output_dir` | string | FU02c output directory. |
| `inputs.c60_edges_csv` | string | Validated C60 edge table. |
| `inputs.c60_nodes_csv` | string | Validated C60 node table. |
| `inputs.c60_faces_csv` | string | Validated C60 face table. |
| `inputs.c60_graph_manifest_json` | string | C60 validation manifest. |
| `carrier_groups.hh_consensus_label` | string | FU02c consensus label for H,H all-representation carriers. |
| `carrier_groups.hp_secondary_label` | string | FU02c consensus label for H,P secondary carriers. |
| `carrier_groups.representation_specific_label` | string | FU02c representation-specific label. |
| `carrier_groups.unstable_label` | string | FU02c unstable/decoy label. |
| `analysis.compute_edge_components` | bool | Whether to compute edge-role components. |
| `analysis.compute_node_junctions` | bool | Whether to compute node junction labels. |
| `analysis.compute_face_involvement` | bool | Whether to compute face-level carrier involvement. |
| `analysis.compute_shell_distance_to_hh_consensus` | bool | Whether to compute edge shell distance to H,H consensus. |
| `analysis.max_shell_distance_reported` | integer | Reporting cap placeholder for shell summaries. |

---

## 3. Carrier edge geometry

Output:

```text
bms_fu02d_carrier_edge_geometry.csv
```

| field name | type | description |
|---|---:|---|
| `edge_key` | string | Canonical edge id. |
| `source` | string | Source node id. |
| `target` | string | Target node id. |
| `edge_type` | string | `6_6` or `5_6`. |
| `shared_face_types` | string | `H,H` or `H,P`. |
| `faces` | string | Incident face ids. |
| `consensus_label` | string | FU02c consensus label. |
| `role_group` | string | `HH_CONSENSUS`, `HP_SECONDARY`, or `OTHER`. |
| `is_hh_consensus` | integer | 1 if H,H consensus carrier. |
| `is_hp_secondary` | integer | 1 if H,P secondary carrier. |
| `is_role_carrier` | integer | 1 if H,H consensus or H,P secondary. |
| `shell_distance_to_hh_consensus` | integer | Edge-adjacency distance to nearest H,H consensus edge. |
| `adjacent_hh_consensus_count` | integer | Number of adjacent H,H consensus edges. |
| `adjacent_hp_secondary_count` | integer | Number of adjacent H,P secondary edges. |
| `adjacent_hh_consensus_edges` | string | Adjacent H,H consensus edge ids. |
| `adjacent_hp_secondary_edges` | string | Adjacent H,P secondary edge ids. |
| `bond_class_weighted_rank` | integer/string | FU02c mean-delta rank in bond-class representation. |
| `topology_only_equal_weight_rank` | integer/string | FU02c mean-delta rank in topology-only representation. |
| `graph_distance_similarity_d3_rank` | integer/string | FU02c mean-delta rank in graph-distance representation. |

---

## 4. Carrier node geometry

Output:

```text
bms_fu02d_carrier_node_geometry.csv
```

| field name | type | description |
|---|---:|---|
| `node_id` | string | C60 node id. |
| `degree` | integer | Graph degree. |
| `incident_hh_consensus_count` | integer | Number of incident H,H consensus carriers. |
| `incident_hp_secondary_count` | integer | Number of incident H,P secondary carriers. |
| `incident_total_carrier_count` | integer | Total incident carrier edges. |
| `carrier_junction_label` | string | Node role label. |
| `incident_hh_consensus_edges` | string | Incident H,H carrier edge ids. |
| `incident_hp_secondary_edges` | string | Incident H,P carrier edge ids. |
| `incident_carrier_edges` | string | Incident carrier edge ids. |

Node role labels:

```text
hh_spine_node
hp_boundary_node
mixed_role_junction
carrier_isolated_endpoint
noncarrier_node
```

---

## 5. Carrier face geometry

Output:

```text
bms_fu02d_carrier_face_geometry.csv
```

| field name | type | description |
|---|---:|---|
| `face_id` | string | Face id. |
| `face_type` | string | `H` or `P`. |
| `incident_edge_count` | integer | Number of incident graph edges. |
| `incident_hh_consensus_edges` | integer | H,H consensus carrier count on face boundary. |
| `incident_hp_secondary_edges` | integer | H,P secondary carrier count on face boundary. |
| `incident_total_carrier_edges` | integer | Total carrier edge count on face boundary. |
| `face_carrier_role_label` | string | Face role label. |
| `hh_consensus_edge_keys` | string | H,H consensus carrier edge ids. |
| `hp_secondary_edge_keys` | string | H,P secondary carrier edge ids. |
| `carrier_edge_keys` | string | All carrier edge ids. |

Face role labels:

```text
hh_patch_face
hp_boundary_face
mixed_patch_boundary_face
carrier_sparse_face
noncarrier_face
```

---

## 6. Carrier component summary

Output:

```text
bms_fu02d_carrier_component_summary.csv
```

| field name | type | description |
|---|---:|---|
| `carrier_group` | string | `HH_CONSENSUS`, `HP_SECONDARY`, or `HH_PLUS_HP`. |
| `component_id` | integer | Component index within carrier group. |
| `component_edge_count` | integer | Number of edges in component. |
| `component_node_count` | integer | Number of nodes in component. |
| `hh_consensus_edge_count` | integer | H,H edge count in component. |
| `hp_secondary_edge_count` | integer | H,P edge count in component. |
| `edge_keys` | string | Component edge ids. |
| `node_ids` | string | Component node ids. |

---

## 7. Carrier role adjacency summary

Output:

```text
bms_fu02d_carrier_role_adjacency_summary.csv
```

| field name | type | description |
|---|---:|---|
| `metric_name` | string | Metric name. |
| `metric_value` | float/string | Metric value. |
| `edge_keys` | string | Relevant edge ids, if applicable. |
| `note` | string | Human-readable metric description. |

Key metrics:

```text
hh_consensus_edge_count
hp_secondary_edge_count
hp_edges_adjacent_to_hh_count
hp_edges_adjacent_to_hh_fraction
hh_edges_with_adjacent_hp_count
hh_edges_with_adjacent_hp_fraction
hp_secondary_shell_distance_<n>_count
```

---

## 8. Visualization edges

Output:

```text
bms_fu02d_visualization_edges.csv
```

| field name | type | description |
|---|---:|---|
| `source` | string | Source node id. |
| `target` | string | Target node id. |
| `edge_key` | string | Canonical edge id. |
| `edge_type` | string | `6_6` or `5_6`. |
| `shared_face_types` | string | `H,H` or `H,P`. |
| `role_group` | string | Visualization role group. |
| `consensus_label` | string | FU02c consensus label. |
| `shell_distance_to_hh_consensus` | integer | Edge shell distance from H,H consensus. |
| `visual_weight` | integer | Suggested visualization line weight. |

---

## 9. Interpretation boundary

Allowed:

```text
FU02d maps carrier-role geometry and patch distribution on the validated C60 graph.
```

Not allowed:

```text
FU02d proves physical spacetime geometry.
```
