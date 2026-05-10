# BMS-FU02g1b — Nanotube Topology Repair Field List

Date: 2026-05-02  
Project: Gravitation und RaumZeit / Quantum-Spacetime-Bridge  
Recommended repo target: `docs/BMS_FU02G1B_NANOTUBE_TOPOLOGY_REPAIR_FIELD_LIST.md`  
Status: Companion field list for BMS-FU02g1b

---

## 1. Purpose

BMS-FU02g1b repairs generated nanotube graph/cell controls before FU02g2.

No carrier diagnostic is run in this block.

---

## 2. Config fields

| field name | type | description |
|---|---:|---|
| `run.run_id` | string | Stable run identifier. |
| `generated_structures.<id>.enabled` | bool | Enables repaired nanotube generation. |
| `generated_structures.<id>.structure_id` | string | Output structure id. |
| `generated_structures.<id>.variant` | string | Tube variant label, e.g. `armchair` or `zigzag`. |
| `generated_structures.<id>.circumference_cells` | integer | Circumferential cell count. |
| `generated_structures.<id>.length_cells` | integer | Axial cell count. |
| `validation.max_allowed_degree` | integer | Maximum allowed graph degree. |
| `validation.require_no_degree4` | bool | Require no degree-4-or-higher nodes. |
| `validation.require_degree3_more_than_degree2` | bool | Require more degree-3 than degree-2 nodes. |
| `validation.require_boundary_not_dominant` | bool | Require boundary nodes not to dominate the graph. |
| `outputs.inventory_csv` | string | Repair inventory CSV path. |
| `outputs.repair_manifest_json` | string | Repair manifest path. |
| `outputs.warnings_json` | string | Warning JSON path. |
| `outputs.resolved_config_yaml` | string | Resolved config path. |
| `naming.output_prefix` | string | Prefix for repaired nanotube artifacts. |

---

## 3. Repair inventory table

Output:

```text
data/bms_fu02g1b_nanotube_topology_repair_inventory.csv
```

| field name | type | description |
|---|---:|---|
| `structure_id` | string | Repaired nanotube structure id. |
| `variant` | string | Variant label. |
| `node_count` | integer | Number of nodes. |
| `edge_count` | integer | Number of edges. |
| `cell_count` | integer | Number of hexagonal cells. |
| `degree_histogram` | JSON string | Degree distribution. |
| `boundary_node_count` | integer | Number of degree-lower boundary nodes. |
| `boundary_edge_count` | integer | Number of one-cell boundary edges. |
| `degree4_count` | integer | Number of degree-4-or-higher nodes. |
| `max_degree` | integer | Maximum graph degree. |
| `validation_status` | string | `valid_for_fu02g2_candidate` or `needs_review`. |
| `geometry_class` | string | Geometry class label. |
| `closure_class` | string | Closure class label. |
| `curvature_class` | string | Curvature proxy label. |
| `diagnostic_scope_note` | string | Scope caveat. |

---

## 4. Node table

Outputs:

```text
data/bms_fu02g1b_<structure_id>_nodes.csv
```

| field name | type | description |
|---|---:|---|
| `structure_id` | string | Parent structure id. |
| `node_id` | string | Repaired node id. |
| `source_node_id` | string | Raw source node ids merged into repaired node. |
| `degree` | integer | Node degree after topology repair. |
| `boundary_node` | integer | 1 if node is boundary-like. |
| `periodic_node` | integer | 1 for cylindrical control nodes. |
| `layout_x` | float | Inspection x coordinate on cylinder. |
| `layout_y` | float | Inspection y coordinate on cylinder. |
| `layout_z` | float | Inspection axial coordinate. |
| `node_role_hint` | string | Non-diagnostic node hint. |
| `coordinate_status` | string | Coordinate caveat. |

---

## 5. Edge table

Outputs:

```text
data/bms_fu02g1b_<structure_id>_edges.csv
```

| field name | type | description |
|---|---:|---|
| `structure_id` | string | Parent structure id. |
| `edge_id` | string | Edge id. |
| `source` | string | Source node. |
| `target` | string | Target node. |
| `source_source_id` | string | Source id provenance. |
| `target_source_id` | string | Target id provenance. |
| `edge_class` | string | Edge class label. |
| `boundary_edge` | integer | 1 if edge has only one incident cell. |
| `periodic_edge` | integer | 1 if edge touches circumferential seam. |
| `cell_left` | string | First incident cell. |
| `cell_right` | string | Second incident cell if available. |
| `cell_count` | integer | Number of incident cells. |
| `edge_role_hint` | string | Non-diagnostic hint. |

---

## 6. Cell table

Outputs:

```text
data/bms_fu02g1b_<structure_id>_cells.csv
```

| field name | type | description |
|---|---:|---|
| `structure_id` | string | Parent structure id. |
| `cell_id` | string | Cell id. |
| `source_cell_id` | string | Source cell id. |
| `cell_type` | string | Cell type; currently `hexagon`. |
| `node_ids` | string | Semicolon-separated repaired node cycle. |
| `edge_ids` | string | Semicolon-separated repaired edge ids. |
| `boundary_cell` | integer | 1 if cell lies at an open tube end. |
| `periodic_cell` | integer | 1 if cell touches circumferential seam. |
| `cell_role_hint` | string | Non-diagnostic cell hint. |
| `layout_x` | float | Inspection x coordinate. |
| `layout_y` | float | Inspection y coordinate. |
| `layout_z` | float | Inspection z coordinate. |
| `coordinate_status` | string | Coordinate caveat. |

---

## 7. Manifest

Outputs:

```text
data/bms_fu02g1b_<structure_id>_manifest.json
data/bms_fu02g1b_nanotube_topology_repair_manifest.json
```

| field name | type | description |
|---|---:|---|
| `run_id` | string | Run id for global manifest. |
| `structure_count` | integer | Number of repaired structures. |
| `structure_ids` | list[string] | Repaired structure ids. |
| `warnings_count` | integer | Number of warnings. |
| `structure_manifests` | object | Per-structure manifests. |
| `validation_status` | string | Per-structure validation status. |
| `degree_histogram` | object | Per-structure degree distribution. |
| `degree4_count` | integer | Per-structure degree-4-or-higher count. |
| `max_degree` | integer | Per-structure max degree. |
| `warnings` | list[string] | Per-structure validation warnings. |

---

## 8. Interpretation boundary

Allowed:

```text
FU02g1b repairs nanotube topology controls for later FU02g2 use.
```

Not allowed:

```text
FU02g1b proves carrier specificity, chemistry or physical nanotube geometry.
```
