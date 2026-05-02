# BMS-FU02f — Runner Field List

Date: 2026-05-02  
Project: Gravitation und RaumZeit / Quantum-Spacetime-Bridge  
Recommended repo target: `docs/BMS_FU02F_RUNNER_FIELD_LIST.md`  
Status: Companion field list for BMS-FU02f visualization and symmetry-orbit inspection

---

## 1. Purpose

BMS-FU02f exports visualization-ready node/edge/face tables and performs conservative graph-level shape/orbit inspection of the compact role-balanced C60 carrier region.

Core question:

```text
Wie sieht der kompakte 17-Face-Klunker im C60-Käfig aus?
```

---

## 2. Config fields

| field name | type | description |
|---|---:|---|
| `run.run_id` | string | Stable run identifier. |
| `run.output_dir` | string | Output directory. |
| `inputs.fu02d1_output_dir` | string | FU02d1 output directory. |
| `inputs.fu02d_output_dir` | string | FU02d output directory. |
| `inputs.fu02e1_output_dir` | string | FU02e1 output directory. |
| `inputs.c60_edges_csv` | string | Validated C60 edge table. |
| `inputs.c60_nodes_csv` | string | Validated C60 node table. |
| `inputs.c60_faces_csv` | string | Validated C60 face table. |
| `inputs.c60_graph_manifest_json` | string | C60 validation manifest. |
| `shape_diagnostics.enable_face_id_run_diagnostics` | bool | Enables weak face-id interval diagnostics. |
| `shape_diagnostics.enable_face_adjacency_boundary_diagnostics` | bool | Enables carrier boundary/internal face-adjacency diagnostics. |
| `shape_diagnostics.enable_distance_to_mixed_core` | bool | Enables face distance to mixed-core diagnostics. |
| `visualization.write_simple_svg` | bool | Writes simple non-geometric SVG face map. |
| `visualization.svg_width` | integer | SVG width. |
| `visualization.svg_height` | integer | SVG height. |

---

## 3. Visualization nodes

Output:

```text
bms_fu02f_visualization_nodes.csv
```

| field name | type | description |
|---|---:|---|
| `node_id` | string | C60 node id. |
| `degree` | integer | Graph degree. |
| `node_role_label` | string | FU02d node role label. |
| `incident_hh_consensus_count` | integer | Incident H,H consensus edge count. |
| `incident_hp_secondary_count` | integer | Incident H,P secondary edge count. |
| `incident_total_carrier_count` | integer | Total incident carrier edge count. |
| `carrier_region_member` | integer | 1 if node is part of carrier region. |
| `visual_size` | float/integer | Suggested visualization size. |
| `visual_layer` | integer | Suggested visualization layer. |

---

## 4. Visualization edges

Output:

```text
bms_fu02f_visualization_edges.csv
```

| field name | type | description |
|---|---:|---|
| `edge_key` | string | Canonical edge id. |
| `source` | string | Source node id. |
| `target` | string | Target node id. |
| `edge_type` | string | `6_6` or `5_6`. |
| `shared_face_types` | string | `H,H` or `H,P`. |
| `carrier_role` | string | `HH_CONSENSUS`, `HP_SECONDARY`, or `OTHER`. |
| `is_hh_consensus` | integer | 1 if H,H consensus edge. |
| `is_hp_secondary` | integer | 1 if H,P secondary edge. |
| `is_role_carrier` | integer | 1 if carrier edge. |
| `shell_distance_to_hh_consensus` | integer | Edge shell distance to nearest H,H consensus edge. |
| `visual_weight` | float/integer | Suggested edge weight. |
| `visual_layer` | integer | Suggested edge layer. |

---

## 5. Visualization faces

Output:

```text
bms_fu02f_visualization_faces.csv
```

| field name | type | description |
|---|---:|---|
| `face_id` | string | Face id. |
| `face_type` | string | `H` or `P`. |
| `face_carrier_role_label` | string | FU02d1 face role label. |
| `carrier_edge_count` | integer | Carrier edge count on face. |
| `hh_consensus_edge_count` | integer | H,H consensus edge count on face. |
| `hp_secondary_edge_count` | integer | H,P secondary edge count on face. |
| `mixed_role_junction_node_count` | integer | Mixed junction node count on face. |
| `carrier_region_member` | integer | 1 if carrier face. |
| `face_distance_to_mixed_core` | integer | Face-adjacency distance to nearest mixed seam-boundary face. |
| `visual_weight` | float/integer | Suggested face weight. |
| `visual_layer` | integer | Suggested face layer. |
| `carrier_edge_keys` | string | Carrier edges on face. |
| `boundary_node_ids` | string | Boundary nodes inferred from face edges. |

---

## 6. Region manifest

Output:

```text
bms_fu02f_region_manifest.json
```

| field name | type | description |
|---|---:|---|
| `carrier_face_ids` | list[string] | Carrier faces. |
| `mixed_face_ids` | list[string] | Mixed seam-boundary faces. |
| `hp_boundary_face_ids` | list[string] | H/P boundary faces. |
| `carrier_adjacent_face_ids` | list[string] | Noncarrier faces adjacent to carrier region. |
| `noncarrier_face_ids` | list[string] | Noncarrier faces. |
| `carrier_node_ids` | list[string] | Carrier nodes. |
| `carrier_edge_ids` | list[string] | Carrier edges. |
| `hh_consensus_edges` | list[string] | H,H consensus carrier edges. |
| `hp_secondary_edges` | list[string] | H,P secondary carrier edges. |

---

## 7. Symmetry/orbit inspection

Output:

```text
bms_fu02f_symmetry_orbit_inspection.csv
```

| field name | type | description |
|---|---:|---|
| `diagnostic_name` | string | Diagnostic id. |
| `diagnostic_value` | string/float/integer | Diagnostic value. |
| `note` | string | Interpretation caveat or explanation. |

Diagnostics include:

```text
carrier_hexagon_intervals
carrier_pentagon_intervals
mixed_face_intervals
carrier_face_internal_adjacency_count
carrier_face_boundary_adjacency_count
carrier_face_external_neighbor_count
max_distance_to_mixed_core
mean_distance_to_mixed_core
```

---

## 8. Shape diagnostic summary

Output:

```text
bms_fu02f_shape_diagnostic_summary.json
```

Key fields:

| field name | type | description |
|---|---:|---|
| `face_count` | integer | Total face count. |
| `carrier_face_count` | integer | Number of carrier faces. |
| `carrier_face_fraction` | float | Carrier face fraction. |
| `carrier_hexagon_count` | integer | Carrier hexagon count. |
| `carrier_pentagon_count` | integer | Carrier pentagon count. |
| `mixed_core_face_count` | integer | Mixed core face count. |
| `hp_boundary_face_count` | integer | H/P boundary face count. |
| `carrier_face_internal_adjacency_count` | integer | Internal face adjacencies within carrier region. |
| `carrier_face_boundary_adjacency_count` | integer | Boundary adjacencies from carrier to noncarrier faces. |
| `max_distance_to_mixed_core` | integer | Max carrier-face distance to mixed core. |
| `mean_distance_to_mixed_core` | float | Mean carrier-face distance to mixed core. |
| `carrier_hexagon_intervals` | string | Weak face-id interval cue. |
| `carrier_pentagon_intervals` | string | Weak face-id interval cue. |
| `mixed_face_intervals` | string | Weak face-id interval cue. |
| `shape_label` | string | Conservative descriptive label. |
| `scope_note` | string | Scope caveat. |

---

## 9. Simple SVG

Output:

```text
bms_fu02f_simple_region_map.svg
```

Important caveat:

```text
This is a non-geometric face-id map for inspection only, not a true 3D C60
projection.
```

---

## 10. Interpretation boundary

Allowed:

```text
FU02f makes the carrier-role region inspectable and gives conservative
graph-shape diagnostics.
```

Not allowed:

```text
FU02f proves physical spacetime, a physical belt, or full C60 automorphism orbit
recovery.
```
