# BMS-FU02g1 — Structure Inventory Builder Field List

Date: 2026-05-02  
Project: Gravitation und RaumZeit / Quantum-Spacetime-Bridge  
Recommended repo target: `docs/BMS_FU02G1_STRUCTURE_INVENTORY_BUILDER_FIELD_LIST.md`  
Status: Companion field list for BMS-FU02g1

---

## 1. Purpose

BMS-FU02g1 builds graph/cell inventory artifacts for real-structure memory and
symmetry-control tests.

No carrier-specificity claim is made in this block.

---

## 2. Config fields

| field name | type | description |
|---|---:|---|
| `run.run_id` | string | Stable run identifier. |
| `inputs.c60_nodes_csv` | string | Existing C60 node table from FU01. |
| `inputs.c60_edges_csv` | string | Existing C60 edge table from FU01. |
| `inputs.c60_faces_csv` | string | Existing C60 face table from FU01. |
| `inputs.c60_manifest_json` | string | Existing C60 validation manifest from FU01. |
| `generated_structures.graphene_patch.enabled` | bool | Enables generated graphene-patch control. |
| `generated_structures.graphene_patch.rows` | integer | Patch rows. |
| `generated_structures.graphene_patch.cols` | integer | Patch columns. |
| `generated_structures.graphene_patch.structure_id` | string | Structure id. |
| `generated_structures.nanotube_armchair.enabled` | bool | Enables generated armchair nanotube control. |
| `generated_structures.nanotube_armchair.circumference_cells` | integer | Circumferential cell count. |
| `generated_structures.nanotube_armchair.length_cells` | integer | Axial cell count. |
| `generated_structures.nanotube_armchair.structure_id` | string | Structure id. |
| `generated_structures.nanotube_zigzag.enabled` | bool | Enables generated zigzag nanotube control. |
| `generated_structures.nanotube_zigzag.circumference_cells` | integer | Circumferential cell count. |
| `generated_structures.nanotube_zigzag.length_cells` | integer | Axial cell count. |
| `generated_structures.nanotube_zigzag.structure_id` | string | Structure id. |
| `outputs.inventory_csv` | string | Inventory CSV output path. |
| `outputs.inventory_manifest_json` | string | Inventory manifest output path. |
| `outputs.warnings_json` | string | Warning JSON output path. |
| `outputs.resolved_config_yaml` | string | Resolved config output path. |
| `naming.output_prefix` | string | Prefix for generated structure-specific artifacts. |

---

## 3. Inventory table

Output:

```text
data/bms_fu02g_structure_inventory.csv
```

| field name | type | description |
|---|---:|---|
| `structure_id` | string | Stable structure id. |
| `structure_class` | string | Structure family label. |
| `geometry_class` | string | Geometry-class label. |
| `node_count` | integer | Number of nodes. |
| `edge_count` | integer | Number of edges. |
| `cell_count` | integer | Number of cells/faces. |
| `boundary_present` | bool/string | Whether finite/open boundary exists. |
| `boundary_node_count` | integer | Number of boundary nodes. |
| `boundary_edge_count` | integer | Number of boundary edges. |
| `periodic_dimension_count` | integer | Number of periodic/identified dimensions. |
| `closure_class` | string | Open/closed/cylindrical closure label. |
| `curvature_class` | string | Curvature proxy label. |
| `pentagon_present` | bool/string | Whether pentagon cells are present. |
| `hexagon_present` | bool/string | Whether hexagon cells are present. |
| `chirality_label` | string | Chirality/wrapping label. |
| `inversion_flag` | bool/string | Inversion-symmetry indicator or proxy label. |
| `rotation_symmetry_label` | string | Rotation-symmetry label. |
| `reflection_flag` | bool/string | Reflection-symmetry indicator or proxy label. |
| `screw_symmetry_flag` | bool/string | Screw-symmetry indicator or proxy label. |
| `source_type` | string | Validated reference or generated graph control. |
| `source_note` | string | Human-readable source/generation note. |
| `layout_coordinate_status` | string | Coordinate status. |
| `diagnostic_scope_note` | string | Scope caveat. |

---

## 4. Node table

Outputs:

```text
data/bms_fu02g_<structure_id>_nodes.csv
```

| field name | type | description |
|---|---:|---|
| `structure_id` | string | Parent structure id. |
| `node_id` | string | Normalized node id. |
| `source_node_id` | string | Original/source node id. |
| `degree` | integer | Node degree in graph. |
| `boundary_node` | integer | 1 if node is boundary node. |
| `periodic_node` | integer | 1 if node belongs to periodic/identified generated control. |
| `layout_x` | float | Inspection/layout x coordinate. |
| `layout_y` | float | Inspection/layout y coordinate. |
| `layout_z` | float | Inspection/layout z coordinate. |
| `node_role_hint` | string | Non-diagnostic role hint. |
| `coordinate_status` | string | Coordinate-status caveat. |

---

## 5. Edge table

Outputs:

```text
data/bms_fu02g_<structure_id>_edges.csv
```

| field name | type | description |
|---|---:|---|
| `structure_id` | string | Parent structure id. |
| `edge_id` | string | Normalized edge id. |
| `source` | string | Source node id. |
| `target` | string | Target node id. |
| `source_source_id` | string | Original/source id for source. |
| `target_source_id` | string | Original/source id for target. |
| `edge_class` | string | Edge class / proxy class. |
| `boundary_edge` | integer | 1 if edge belongs to open boundary. |
| `periodic_edge` | integer | 1 if edge belongs to periodic/circumferential join. |
| `cell_left` | string | First incident cell if available. |
| `cell_right` | string | Second incident cell if available. |
| `cell_count` | integer | Number of incident cells. |
| `edge_role_hint` | string | Non-diagnostic edge role hint. |

---

## 6. Cell table

Outputs:

```text
data/bms_fu02g_<structure_id>_cells.csv
```

| field name | type | description |
|---|---:|---|
| `structure_id` | string | Parent structure id. |
| `cell_id` | string | Normalized cell id. |
| `source_cell_id` | string | Original/source cell id. |
| `cell_type` | string | Cell type, e.g. hexagon/pentagon. |
| `node_ids` | string | Semicolon-separated node cycle ids. |
| `edge_ids` | string | Semicolon-separated edge ids. |
| `boundary_cell` | integer | 1 if cell touches open finite boundary. |
| `periodic_cell` | integer | 1 if cell touches periodic/circumferential seam. |
| `cell_role_hint` | string | Non-diagnostic cell role hint. |
| `layout_x` | float | Inspection/layout x coordinate. |
| `layout_y` | float | Inspection/layout y coordinate. |
| `layout_z` | float | Inspection/layout z coordinate. |
| `coordinate_status` | string | Coordinate-status caveat. |

---

## 7. Structure manifest

Outputs:

```text
data/bms_fu02g_<structure_id>_manifest.json
```

| field name | type | description |
|---|---:|---|
| `structure_id` | string | Structure id. |
| `node_count` | integer | Number of nodes. |
| `edge_count` | integer | Number of edges. |
| `cell_count` | integer | Number of cells. |
| `boundary_node_count` | integer | Number of boundary nodes. |
| `boundary_edge_count` | integer | Number of boundary edges. |
| `degree_histogram` | object | Degree distribution. |
| `cell_type_counts` | object | Cell type counts. |
| `boundary_present` | bool/string | Boundary flag. |
| `periodic_dimension_count` | integer | Periodic dimension count. |
| `closure_class` | string | Closure label. |
| `curvature_class` | string | Curvature proxy. |
| `hexagon_present` | bool/string | Hexagon presence flag. |
| `pentagon_present` | bool/string | Pentagon presence flag. |
| `validation_status` | string | `valid` or `valid_with_warnings`. |
| `warnings` | list[string] | Structure-specific warnings. |
| `scope_note` | string | Scope caveat. |
| `meta` | object | Metadata used to create inventory row. |

---

## 8. Interpretation boundary

Allowed:

```text
FU02g1 builds graph/cell inventory controls.
```

Not allowed:

```text
FU02g1 proves carrier specificity, molecular geometry, quantum chemistry or
spacetime physics.
```
