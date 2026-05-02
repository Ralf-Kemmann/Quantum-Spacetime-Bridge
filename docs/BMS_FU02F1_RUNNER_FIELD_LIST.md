# BMS-FU02f1 — Runner Field List

Date: 2026-05-02  
Project: Gravitation und RaumZeit / Quantum-Spacetime-Bridge  
Recommended repo target: `docs/BMS_FU02F1_RUNNER_FIELD_LIST.md`  
Status: Companion field list for BMS-FU02f1 face-id interval repair and graph-layout export

---

## 1. Purpose

BMS-FU02f1 repairs FU02f face-id interval diagnostics and exports deterministic layout-ready artifacts for inspecting the compact role-balanced C60 carrier region.

Core question:

```text
Ist die Karte jetzt sauber und layout-fähig?
```

---

## 2. Config fields

| field name | type | description |
|---|---:|---|
| `run.run_id` | string | Stable run identifier. |
| `run.output_dir` | string | Output directory. |
| `inputs.fu02f_output_dir` | string | FU02f output directory. |
| `inputs.c60_edges_csv` | string | Validated C60 edge table. |
| `inputs.c60_nodes_csv` | string | Validated C60 node table. |
| `inputs.c60_faces_csv` | string | Validated C60 face table. |
| `inputs.c60_graph_manifest_json` | string | C60 validation manifest. |
| `layout.face_layout_mode` | string | Face layout strategy. |
| `layout.node_layout_mode` | string | Node layout strategy. |
| `layout.svg_width` | integer | SVG width. |
| `layout.svg_height` | integer | SVG height. |

---

## 3. Repaired interval summary

Output:

```text
bms_fu02f1_repaired_interval_summary.json
```

| field name | type | description |
|---|---:|---|
| `carrier_hexagon_intervals` | string | Repaired generated-id intervals for carrier hexagons. |
| `carrier_pentagon_intervals` | string | Repaired generated-id intervals for carrier pentagons. |
| `mixed_face_intervals` | string | Repaired generated-id intervals for mixed faces. |
| `hp_boundary_face_intervals` | string | Repaired generated-id intervals for H/P boundary faces. |
| `carrier_adjacent_face_intervals` | string | Repaired generated-id intervals for adjacent faces. |
| `noncarrier_face_intervals` | string | Repaired generated-id intervals for noncarrier faces. |
| `carrier_face_count` | integer | Carrier face count. |
| `mixed_face_count` | integer | Mixed face count. |
| `hp_boundary_face_count` | integer | H/P boundary face count. |
| `carrier_adjacent_face_count` | integer | Adjacent face count. |
| `noncarrier_face_count` | integer | Noncarrier face count. |
| `scope_note` | string | Caveat that face-id intervals are generated-id diagnostics only. |

---

## 4. Face layout

Output:

```text
bms_fu02f1_face_layout.csv
```

| field name | type | description |
|---|---:|---|
| `face_id` | string | Face id. |
| `face_type` | string | Face type, usually `H` or `P`. |
| `face_carrier_role_label` | string | Face role label. |
| `carrier_edge_count` | integer | Carrier edge count. |
| `hh_consensus_edge_count` | integer | H,H carrier edge count. |
| `hp_secondary_edge_count` | integer | H/P carrier edge count. |
| `mixed_role_junction_node_count` | integer | Mixed node count. |
| `face_distance_to_mixed_core` | integer | Face distance to mixed core. |
| `layout_x` | float | Inspection layout x coordinate. |
| `layout_y` | float | Inspection layout y coordinate. |
| `layout_radius` | float | Role-shell radius. |
| `layout_angle_rad` | float | Layout angle in radians. |
| `layout_role_shell` | string | Role shell label. |
| `visual_layer` | integer | Suggested visual layer. |
| `visual_color_hint` | string | Suggested color. |
| `layout_scope_note` | string | Layout caveat. |

---

## 5. Node layout

Output:

```text
bms_fu02f1_node_layout.csv
```

| field name | type | description |
|---|---:|---|
| `node_id` | string | C60 node id. |
| `node_role_label` | string | Node role label. |
| `carrier_region_member` | integer | 1 if node is part of carrier region. |
| `layout_x` | float | Deterministic inspection x coordinate. |
| `layout_y` | float | Deterministic inspection y coordinate. |
| `layout_z` | float | Deterministic inspection z coordinate. |
| `layout_scope_note` | string | Caveat: not physical C60 coordinates. |

---

## 6. Edge layout

Output:

```text
bms_fu02f1_edge_layout.csv
```

| field name | type | description |
|---|---:|---|
| `edge_key` | string | Canonical edge id. |
| `source` | string | Source node id. |
| `target` | string | Target node id. |
| `carrier_role` | string | Carrier role label. |
| `edge_type` | string | Edge type. |
| `shared_face_types` | string | Shared face types. |
| `source_layout_x` | float | Source layout x. |
| `source_layout_y` | float | Source layout y. |
| `source_layout_z` | float | Source layout z. |
| `target_layout_x` | float | Target layout x. |
| `target_layout_y` | float | Target layout y. |
| `target_layout_z` | float | Target layout z. |
| `layout_scope_note` | string | Layout caveat. |

---

## 7. Graph layout manifest

Output:

```text
bms_fu02f1_graph_layout_manifest.json
```

| field name | type | description |
|---|---:|---|
| `face_layout_mode` | string | Face layout mode. |
| `node_layout_mode` | string | Node layout mode. |
| `face_interval_repair_success` | bool | Whether required interval fields are nonempty. |
| `interval_summary` | object | Repaired interval summary. |
| `layout_scope_note` | string | Layout caveat. |

---

## 8. SVG

Output:

```text
bms_fu02f1_repaired_region_map.svg
```

Important caveat:

```text
Role-shell circular inspection layout only; not physical C60 geometry.
```

---

## 9. Interpretation boundary

Allowed:

```text
FU02f1 repairs interval diagnostics and exports layout-ready inspection artifacts.
```

Not allowed:

```text
FU02f1 proves physical C60 geometry, physical spacetime, or full symmetry-orbit recovery.
```
