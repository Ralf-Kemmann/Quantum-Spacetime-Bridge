# BMS-FU01b — Runner Field List

Date: 2026-05-01  
Project: Gravitation und RaumZeit / Quantum-Spacetime-Bridge  
Recommended repo target: `docs/BMS_FU01B_RUNNER_FIELD_LIST.md`  
Status: Companion field list for BMS-FU01b C60 core-selection sensitivity diagnostic

---

## 1. Purpose

BMS-FU01b tests whether the BMS-FU01 result depends on one deterministic local 6:6 reference-core patch, or whether comparable behavior survives under alternative C60 core selections.

Working question:

```text
Ist FU01 nur eine lokale Nahtstelle,
oder trägt die C60-Struktur auch bei anders gewählten Core-Schnitten?
```

---

## 2. Config fields

| field name | type | description |
|---|---:|---|
| `run.run_id` | string | Stable run identifier. |
| `run.output_dir` | string | Output directory. |
| `run.random_seed` | integer | Seed for null generation. |
| `inputs.nodes_csv` | string | Validated C60 node artifact. |
| `inputs.edges_csv` | string | Validated C60 edge artifact. |
| `inputs.faces_csv` | string | Validated C60 face artifact. |
| `inputs.graph_manifest_json` | string | Builder manifest with C60 validation checks. |
| `core_variants[].core_variant_id` | string | Core variant label. |
| `core_variants[].mode` | string | Core selection mode. |
| `core_variants[].edge_type` | string | Selected edge type, e.g. `6_6` or `5_6`. |
| `core_variants[].edge_count` | integer | Number of core edges. |
| `core_variants[].description` | string | Human-readable purpose of core variant. |

---

## 3. Core variants

FU01b-v0 uses four deterministic variants:

| field name | type | description |
|---|---:|---|
| `local_6_6_patch_core` | core variant | FU01-v0 continuity core: first sorted 6:6 edges. |
| `distributed_6_6_core` | core variant | Evenly spaced 6:6 edges across sorted 6:6 edge list. |
| `local_5_6_pentagon_boundary_core` | core variant | First sorted 5:6 pentagon-boundary edges. |
| `distributed_5_6_pentagon_boundary_core` | core variant | Evenly spaced 5:6 pentagon-boundary edges across sorted 5:6 edge list. |

---

## 4. Core variants table

Output:

```text
bms_fu01b_core_variants.csv
```

| field name | type | description |
|---|---:|---|
| `core_variant_id` | string | Core variant label. |
| `core_variant_mode` | string | Selection mode. |
| `description` | string | Human-readable core description. |
| `selection_rule` | string | Concrete deterministic rule. |
| `edge_count` | integer | Number of selected core edges. |
| `node_count` | integer | Number of nodes touched by core. |
| `edge_type_counts` | JSON string | Counts of `5_6` and/or `6_6` core edges. |
| `face_span_count` | integer | Number of unique faces touched by core. |
| `pentagon_face_span_count` | integer | Number of unique pentagon faces touched. |
| `hexagon_face_span_count` | integer | Number of unique hexagon faces touched. |
| `face_type_incidence_counts` | JSON string | Face-type incidence counts across core edges. |
| `connected_component_count` | integer | Connected components inside core-induced edge set. |

---

## 5. Reference core edges table

Output:

```text
bms_fu01b_reference_core_edges.csv
```

| field name | type | description |
|---|---:|---|
| `core_variant_id` | string | Core variant label. |
| `core_variant_mode` | string | Core selection mode. |
| `core_edge_rank` | integer | Rank/order within selected core. |
| `source` | string | Source node id. |
| `target` | string | Target node id. |
| `edge_type` | string | Edge type. |
| `weight` | float | Structural weight. |
| `shared_faces` | string | Shared face ids. |
| `shared_face_types` | string | Shared face types. |
| `reference_core_rule` | string | Selection rule. |

---

## 6. Edge output table

Output:

```text
bms_fu01b_edges.csv
```

| field name | type | description |
|---|---:|---|
| `core_variant_id` | string | Core variant used for this object. |
| `object_id` | string | Real/null object id. |
| `null_family` | string | Null family label or `real`. |
| `repeat_index` | integer/string | Repeat index or `real`. |
| `edge_id` | string | Edge id where available. |
| `source` | string | Source node id. |
| `target` | string | Target node id. |
| `edge_type` | string | Edge class, e.g. `5_6` or `6_6`. |
| `source_degree` | integer-like | Source node degree. |
| `target_degree` | integer-like | Target node degree. |
| `shared_face_count` | integer-like | Number of shared incident faces. |
| `shared_faces` | string | Incident face ids. |
| `shared_face_types` | string | Face-type pair, e.g. `H,H` or `H,P`. |
| `weight` | float | Structural edge weight. |
| `distance` | float | Derived distance proxy. |
| `comment` | string | Methodological note. |

---

## 7. Metric tables

Outputs:

```text
bms_fu01b_core_metrics.csv
bms_fu01b_envelope_metrics.csv
```

| field name | type | description |
|---|---:|---|
| `core_variant_id` | string | Core variant label. |
| `object_id` | string | Real/null object id. |
| `null_family` | string | Null family label or `real`. |
| `repeat_index` | integer/string | Repeat index or `real`. |
| `construction_family` | string | Construction family. |
| `construction_variant` | string | Construction variant. |
| `edge_count` | integer | Number of edges in constructed envelope. |
| `node_count` | integer | Number of nodes touched by constructed envelope. |
| `metric_name` | string | Metric name. |
| `metric_value` | float | Metric value. |

Metrics:

| field name | type | description |
|---|---:|---|
| `envelope_core_edge_containment` | float | Fraction of current reference-core edges recovered. |
| `envelope_core_node_containment` | float | Fraction of current reference-core nodes recovered. |
| `edge_type_6_6_fraction` | float | Fraction of selected edges assigned `6_6`. |
| `edge_type_5_6_fraction` | float | Fraction of selected edges assigned `5_6`. |
| `connected_component_count` | float | Number of connected components in selected envelope. |

---

## 8. Real-vs-null summary

Output:

```text
bms_fu01b_real_vs_null_summary.csv
```

| field name | type | description |
|---|---:|---|
| `core_variant_id` | string | Core variant label. |
| `null_family` | string | Null family summarized. |
| `metric_name` | string | Metric name. |
| `construction_family` | string | Construction family. |
| `construction_variant` | string | Construction variant. |
| `real_value` | float | Real graph metric value. |
| `null_mean` | float | Mean null metric value. |
| `null_min` | float | Minimum null metric value. |
| `null_max` | float | Maximum null metric value. |
| `real_minus_null_mean` | float | Real value minus null mean. |
| `empirical_exceedance_fraction` | float | Fraction of null repeats greater than or equal to real value. |
| `null_count` | integer | Number of null repeats. |
| `interpretation_label` | string | Conservative interpretation label. |

---

## 9. Core variant summary

Output:

```text
bms_fu01b_core_variant_summary.csv
```

| field name | type | description |
|---|---:|---|
| `core_variant_id` | string | Core variant label. |
| `null_family` | string | Null family summarized. |
| `core_variant_mode` | string | Core selection mode. |
| `edge_type_counts` | JSON string | Core edge-type composition. |
| `face_span_count` | integer-like | Number of faces touched by core. |
| `connected_component_count` | integer-like | Connected components inside core. |
| `summary_row_count` | integer | Number of summary rows for this group. |
| `label_counts` | JSON string | Counts by interpretation label. |
| `core_metric_real_exceeds_count` | integer | Core-metric rows labeled real-exceeds. |
| `core_metric_null_reproduces_count` | integer | Core-metric rows labeled null-reproduces-core. |

---

## 10. Null family inventory

Output:

```text
bms_fu01b_null_family_inventory.csv
```

| field name | type | description |
|---|---:|---|
| `core_variant_id` | string | Core variant label. |
| `object_id` | string | Null object id. |
| `null_family` | string | Null family label. |
| `repeat_index` | integer | Repeat index. |

---

## 11. Interpretation boundary

Allowed:

```text
BMS-FU01b tests whether the FU01 C60 result is robust under alternative local
and distributed 6:6 / 5:6 core selections.
```

Not allowed:

```text
C60 proves emergent spacetime.
The bridge recognizes molecules.
A physical metric has been recovered.
Fullerene symmetry is proven as spacetime structure.
Quantum chemistry has been reproduced.
```
