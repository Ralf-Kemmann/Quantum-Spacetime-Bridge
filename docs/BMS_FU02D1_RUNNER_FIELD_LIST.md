# BMS-FU02d1 — Runner Field List

Date: 2026-05-02  
Project: Gravitation und RaumZeit / Quantum-Spacetime-Bridge  
Recommended repo target: `docs/BMS_FU02D1_RUNNER_FIELD_LIST.md`  
Status: Companion field list for BMS-FU02d1 face parser repair and face-level localization

---

## 1. Purpose

BMS-FU02d1 repairs the FU02d-v0 face-level parser and maps the FU02d seam-boundary carrier network onto C60 faces.

Core question:

```text
Auf welchen Faces liegt das 30-edge / 25-node Carrier-Netz?
```

---

## 2. Config fields

| field name | type | description |
|---|---:|---|
| `run.run_id` | string | Stable run identifier. |
| `run.output_dir` | string | Output directory. |
| `inputs.fu02d_output_dir` | string | FU02d output directory. |
| `inputs.fu02c_output_dir` | string | FU02c output directory. |
| `inputs.c60_edges_csv` | string | Validated C60 edge table. |
| `inputs.c60_nodes_csv` | string | Validated C60 node table. |
| `inputs.c60_faces_csv` | string | Validated C60 face table. |
| `inputs.c60_graph_manifest_json` | string | C60 validation manifest. |
| `parser.edge_face_column_candidates.paired` | list[list[string]] | Candidate paired edge-to-face columns. |
| `parser.edge_face_column_candidates.list_like` | list[string] | Candidate list-like edge-to-face columns. |
| `parser.face_node_column_candidates` | list[string] | Candidate face node-cycle columns. |
| `carrier_groups.hh_consensus_label` | string | FU02c/FU02d H,H consensus label. |
| `carrier_groups.hp_secondary_label` | string | FU02c/FU02d H,P secondary label. |

---

## 3. Face parser audit

Output:

```text
bms_fu02d1_face_parser_audit.json
```

| field name | type | description |
|---|---:|---|
| `detected_edge_face_columns` | list[string] | Edge table columns used for face incidence. |
| `detected_face_node_column` | string | Face table node-cycle column used if edge table did not contain face columns. |
| `edge_face_mapping_source` | string | Mapping source, e.g. `edge_table_paired_columns`, `edge_table_list_column`, or `face_table_node_cycle_reconstruction`. |
| `mapped_edge_count` | integer | Number of C60 edges mapped to faces. |
| `unmapped_edge_count` | integer | Number of C60 edges without face mapping. |
| `face_count` | integer | Number of faces inspected. |
| `warnings` | list[string] | Parser-specific warnings. |

---

## 4. Face localization

Output:

```text
bms_fu02d1_face_localization.csv
```

| field name | type | description |
|---|---:|---|
| `face_id` | string | Face id. |
| `face_type` | string | `H` for hexagon, `P` for pentagon, or empty if unresolved. |
| `boundary_edge_count` | integer | Number of boundary edges mapped to the face. |
| `hh_consensus_edge_count` | integer | Number of H,H consensus carrier edges on this face. |
| `hp_secondary_edge_count` | integer | Number of H,P secondary carrier edges on this face. |
| `carrier_edge_count` | integer | Total H,H/H,P carrier edges on this face. |
| `mixed_role_junction_node_count` | integer | Number of FU02d mixed-role junction nodes on this face boundary. |
| `carrier_node_count` | integer | Number of carrier-involved nodes on this face boundary. |
| `face_carrier_role_label` | string | Face role label. |
| `hh_consensus_edge_keys` | string | H,H carrier edge ids on face. |
| `hp_secondary_edge_keys` | string | H,P carrier edge ids on face. |
| `carrier_edge_keys` | string | All carrier edge ids on face. |
| `boundary_edge_keys` | string | All mapped boundary edge ids on face. |
| `boundary_node_ids` | string | Boundary node ids inferred from boundary edges. |

Face role labels:

```text
hh_seam_face
hp_boundary_face
mixed_seam_boundary_face
carrier_adjacent_face
noncarrier_face
parser_unresolved_face
```

---

## 5. Face component summary

Output:

```text
bms_fu02d1_face_component_summary.csv
```

| field name | type | description |
|---|---:|---|
| `face_group` | string | `HH_FACE_SET`, `HP_FACE_SET`, `MIXED_FACE_SET`, or `CARRIER_FACE_SET`. |
| `component_id` | integer | Component id within face group. |
| `component_face_count` | integer | Number of faces in component. |
| `hexagon_count` | integer | Number of hexagon faces in component. |
| `pentagon_count` | integer | Number of pentagon faces in component. |
| `hh_consensus_edge_count` | integer | H,H carrier edge incidence count across component. |
| `hp_secondary_edge_count` | integer | H,P carrier edge incidence count across component. |
| `carrier_edge_count` | integer | Total carrier edge incidence count across component. |
| `mixed_role_junction_node_count` | integer | Mixed-role junction incidence count across component. |
| `face_ids` | string | Face ids in the component. |

---

## 6. Face adjacency edges

Output:

```text
bms_fu02d1_face_adjacency_edges.csv
```

| field name | type | description |
|---|---:|---|
| `edge_key` | string | C60 edge shared by two faces. |
| `face_a` | string | First face id. |
| `face_b` | string | Second face id. |
| `face_a_type` | string | First face type. |
| `face_b_type` | string | Second face type. |

---

## 7. Carrier face summary

Output:

```text
bms_fu02d1_carrier_face_summary.csv
```

| field name | type | description |
|---|---:|---|
| `metric_name` | string | Summary metric name. |
| `metric_value` | string/float/integer | Summary metric value. |
| `note` | string | Human-readable explanation. |

Key metrics:

```text
face_parser_source
mapped_edge_count
unmapped_edge_count
carrier_face_count
carrier_face_fraction
carrier_face_component_count
largest_carrier_face_component_count
region_label
face_label_count__*
carrier_face_type_count__*
```

---

## 8. Visualization faces

Output:

```text
bms_fu02d1_visualization_faces.csv
```

| field name | type | description |
|---|---:|---|
| `face_id` | string | Face id. |
| `face_type` | string | Face type. |
| `face_carrier_role_label` | string | Face role label. |
| `carrier_edge_count` | integer | Number of carrier edges on the face. |
| `hh_consensus_edge_count` | integer | H,H carrier count. |
| `hp_secondary_edge_count` | integer | H,P carrier count. |
| `mixed_role_junction_node_count` | integer | Mixed junction node count. |
| `visual_weight` | integer | Suggested visualization weight. |
| `carrier_edge_keys` | string | Carrier edges on face. |
| `boundary_node_ids` | string | Boundary nodes. |

---

## 9. Interpretation boundary

Allowed:

```text
FU02d1 maps the seam-boundary carrier network onto C60 face incidence.
```

Not allowed without further nulls/visualization:

```text
FU02d1 proves a physical belt or global fullerene symmetry.
```
