# BMS-FU02g2 — Carrier Diagnostic Transfer Field List

Date: 2026-05-02  
Project: Gravitation und RaumZeit / Quantum-Spacetime-Bridge  
Recommended repo target: `docs/BMS_FU02G2_CARRIER_DIAGNOSTIC_TRANSFER_FIELD_LIST.md`  
Status: Companion field list for BMS-FU02g2

---

## 1. Purpose

BMS-FU02g2 transfers a transparent cell-level carrier proxy diagnostic to the
geometry-class control set:

```text
c60_reference
graphene_patch
nanotube_armchair_repaired
nanotube_zigzag_repaired
```

No final real-structure memory claim is made.

---

## 2. Config fields

| field name | type | description |
|---|---:|---|
| `run.run_id` | string | Stable run identifier. |
| `run.output_dir` | string | Output directory. |
| `structures.<id>.enabled` | bool | Enables structure. |
| `structures.<id>.structure_id` | string | Structure id. |
| `structures.<id>.structure_class` | string | Structure class label. |
| `structures.<id>.geometry_class` | string | Geometry class label. |
| `structures.<id>.nodes_csv` | string | Node table path. |
| `structures.<id>.edges_csv` | string | Edge table path. |
| `structures.<id>.cells_csv` | string | Cell table path. |
| `structures.<id>.manifest_json` | string | Manifest path. |
| `optional_reference.c60_fu02f1_face_layout_csv` | string | Optional C60 FU02f1 face-layout reference. |
| `optional_reference.use_if_present` | bool | Use optional C60 reference if file exists. |
| `diagnostic.top_fraction` | float | Fraction of cells selected as carrier cells. |
| `diagnostic.minimum_carrier_cells` | integer | Minimum selected carrier cells. |
| `diagnostic.score_weights.cell_adjacency_degree` | float | Score weight for cell adjacency degree. |
| `diagnostic.score_weights.mean_node_degree` | float | Score weight for mean node degree. |
| `diagnostic.score_weights.two_cell_edge_fraction` | float | Score weight for two-cell edge support. |
| `diagnostic.score_weights.boundary_cell_penalty` | float | Penalty for boundary cells. |
| `diagnostic.score_weights.low_degree_node_fraction_penalty` | float | Penalty for low-degree-node fraction. |

---

## 3. Cell diagnostics table

Output:

```text
runs/BMS-FU02g2/carrier_diagnostic_transfer_geometry_controls_open/bms_fu02g2_cell_diagnostics.csv
```

| field name | type | description |
|---|---:|---|
| `structure_id` | string | Parent structure id. |
| `structure_class` | string | Structure class label. |
| `geometry_class` | string | Geometry class label. |
| `cell_id` | string | Cell id. |
| `cell_type` | string | Cell type, e.g. hexagon/pentagon. |
| `boundary_cell` | integer | 1 if cell is boundary cell. |
| `periodic_cell` | integer/string | Periodic-cell flag from inventory. |
| `cell_adjacency_degree` | float | Degree of cell in cell-adjacency graph. |
| `mean_node_degree` | float | Mean graph-node degree among cell nodes. |
| `low_degree_node_fraction` | float | Fraction of cell nodes with degree below 3. |
| `two_cell_edge_fraction` | float | Fraction of cell edges incident to two cells. |
| `carrier_score` | float | Generalized carrier proxy score. |
| `carrier_rank` | integer | Rank by carrier score within structure. |
| `is_carrier_cell` | integer | 1 if selected as carrier cell. |
| `cell_role_label` | string | Generalized role label. |
| `carrier_component_id` | integer/string | Carrier component id if selected. |
| `distance_to_carrier_core` | integer/string | Cell-adjacency distance to carrier core. |
| `distance_to_boundary` | integer/string | Cell-adjacency distance to boundary cell. |
| `fu02f1_reference_role` | string | Optional C60 FU02f1 role if available. |

---

## 4. Structure summary table

Output:

```text
bms_fu02g2_structure_summary.csv
```

| field name | type | description |
|---|---:|---|
| `structure_id` | string | Structure id. |
| `structure_class` | string | Structure class. |
| `geometry_class` | string | Geometry class. |
| `cell_count` | integer | Total cells. |
| `carrier_cell_count` | integer | Selected carrier cells. |
| `carrier_cell_fraction` | float | Carrier cells / total cells. |
| `carrier_cell_component_count` | integer | Number of carrier components. |
| `largest_carrier_cell_component_count` | integer | Largest carrier component size. |
| `compactness_proxy` | float | Largest carrier component / carrier cells. |
| `boundary_cell_count` | integer | Boundary cells. |
| `boundary_cell_fraction` | float | Boundary cells / total cells. |
| `carrier_boundary_cell_count` | integer | Carrier cells that are boundary cells. |
| `carrier_boundary_overlap_fraction` | float | Boundary carrier cells / carrier cells. |
| `carrier_core_cell_count` | integer | Non-boundary carrier cells. |
| `carrier_adjacent_cell_count` | integer | Noncarrier cells adjacent to carriers. |
| `noncarrier_cell_count` | integer | Cells neither carrier nor adjacent. |
| `cell_adjacency_edge_count` | integer | Edges in cell-adjacency graph. |
| `carrier_internal_adjacency_count` | integer | Cell adjacencies inside carrier set. |
| `carrier_boundary_adjacency_count` | integer | Carrier/noncarrier cell adjacencies. |
| `carrier_external_neighbor_count` | integer | Distinct noncarrier neighbors of carrier set. |
| `max_distance_to_carrier_core` | integer/string | Maximum distance to carrier core. |
| `mean_distance_to_carrier_core` | float/string | Mean distance to carrier core. |
| `carrier_min_distance_to_boundary` | integer/string | Minimum carrier distance to boundary. |
| `carrier_mean_distance_to_boundary` | float/string | Mean carrier distance to boundary. |
| `boundary_dependence_proxy` | float | Carrier boundary overlap fraction. |
| `adjacent_shell_ratio` | float | Adjacent shell size / carrier count. |
| `fu02f1_reference_overlap_count` | integer/string | C60 reference overlap count if available. |
| `fu02f1_reference_overlap_fraction` | float/string | C60 reference overlap fraction if available. |
| `diagnostic_label` | string | Summary interpretation label. |

---

## 5. Geometry-class comparison table

Output:

```text
bms_fu02g2_geometry_class_comparison.csv
```

| field name | type | description |
|---|---:|---|
| `structure_id` | string | Structure id. |
| `geometry_class` | string | Geometry class. |
| `carrier_cell_fraction` | float | Carrier fraction. |
| `compactness_proxy` | float | Compactness proxy. |
| `boundary_dependence_proxy` | float | Boundary dependence proxy. |
| `adjacent_shell_ratio` | float | Adjacent shell ratio. |
| `largest_carrier_component_fraction_of_all_cells` | float | Largest carrier component / total cells. |
| `diagnostic_label` | string | Diagnostic label. |

---

## 6. Run manifest

Output:

```text
bms_fu02g2_run_manifest.json
```

| field name | type | description |
|---|---:|---|
| `run_id` | string | Run id. |
| `structure_count` | integer | Number of processed structures. |
| `structure_ids` | list[string] | Processed structures. |
| `output_dir` | string | Output directory. |
| `cell_diagnostics_csv` | string | Cell diagnostics filename. |
| `structure_summary_csv` | string | Structure summary filename. |
| `geometry_class_comparison_csv` | string | Comparison filename. |
| `c60_fu02f1_reference_loaded` | bool | Whether C60 FU02f1 reference was loaded. |
| `warnings_count` | integer | Warning count. |
| `scope_note` | string | Scope caveat. |

---

## 7. Interpretation boundary

Allowed:

```text
FU02g2 compares carrier-proxy compactness and boundary dependence across
geometry-class controls.
```

Not allowed:

```text
FU02g2 proves real-structure memory, chemistry, spacetime or formal
significance.
```
