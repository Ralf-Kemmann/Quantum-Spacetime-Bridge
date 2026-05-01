# BMS-FU01c — Runner Field List

Date: 2026-05-01  
Project: Gravitation und RaumZeit / Quantum-Spacetime-Bridge  
Recommended repo target: `docs/BMS_FU01C_RUNNER_FIELD_LIST.md`  
Status: Companion field list for BMS-FU01c C60 motif/topology extension

---

## 1. Purpose

BMS-FU01c tests whether the C60 signal remains after removing explicit 6:6 / 5:6 edge-class weights.

Working question:

```text
Bleibt das Signal, wenn wir die 6:6/5:6-Gewichtsinformation herausnehmen?
```

The runner compares:

```text
bond_class_weighted
topology_only_equal_weight
graph_distance_similarity_d3
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
| `representations[].representation_id` | string | Representation variant label. |
| `representations[].edge_mode` | string | `bond_edges_only` or `graph_distance_pairs`. |
| `representations[].weight_rule_id` | string | Weighting rule identifier. |
| `representations[].max_graph_distance` | integer/null | Maximum shortest-path distance included for graph-distance representation. |
| `core_variants[].core_variant_id` | string | Core variant label. |
| `core_variants[].mode` | string | Core selection mode. |
| `core_variants[].edge_type` | string | Selected edge type, e.g. `6_6` or `5_6`. |
| `core_variants[].edge_count` | integer | Number of core edges. |

---

## 3. Representation table

Output:

```text
bms_fu01c_representations.csv
```

| field name | type | description |
|---|---:|---|
| `representation_id` | string | Representation label. |
| `edge_mode` | string | Edge construction mode. |
| `weight_rule_id` | string | Weight rule identifier. |
| `max_graph_distance` | integer/null | Maximum graph distance included. |
| `edge_count` | integer | Number of edges/pairs in representation. |
| `bond_edge_count` | integer | Number of original C60 bond edges. |
| `nonbond_edge_count` | integer | Number of nonbond all-pairs edges. |
| `min_weight` | float | Minimum representation weight. |
| `max_weight` | float | Maximum representation weight. |

---

## 4. Edge output table

Output:

```text
bms_fu01c_edges.csv
```

| field name | type | description |
|---|---:|---|
| `representation_id` | string | Representation label. |
| `core_variant_id` | string | Core variant label. |
| `object_id` | string | Real/null object id. |
| `null_family` | string | Null family label or `real`. |
| `repeat_index` | integer/string | Repeat index or `real`. |
| `edge_id` | string | Edge id where available. |
| `source` | string | Source node id. |
| `target` | string | Target node id. |
| `edge_type` | string | Edge class: `6_6`, `5_6`, or `nonbond`. |
| `source_degree` | integer-like | Source degree where available. |
| `target_degree` | integer-like | Target degree where available. |
| `shared_face_count` | integer-like | Number of shared faces for bond edges. |
| `shared_faces` | string | Shared face ids for bond edges. |
| `shared_face_types` | string | Shared face types for bond edges. |
| `weight` | float | Representation weight. |
| `distance` | float | Derived distance proxy. |
| `graph_distance` | integer | C60 shortest-path distance. |
| `is_bond_edge` | boolean/string | Whether this is an original C60 bond edge. |
| `comment` | string | Methodological note. |

---

## 5. Metric tables

Outputs:

```text
bms_fu01c_core_metrics.csv
bms_fu01c_envelope_metrics.csv
```

| field name | type | description |
|---|---:|---|
| `representation_id` | string | Representation label. |
| `core_variant_id` | string | Core variant label. |
| `object_id` | string | Real/null object id. |
| `null_family` | string | Null family label or `real`. |
| `repeat_index` | integer/string | Repeat index or `real`. |
| `construction_family` | string | Construction family. |
| `construction_variant` | string | Construction variant. |
| `edge_count` | integer | Number of selected envelope edges. |
| `node_count` | integer | Number of selected envelope nodes. |
| `metric_name` | string | Metric name. |
| `metric_value` | float | Metric value. |

Metrics:

| field name | type | description |
|---|---:|---|
| `envelope_core_edge_containment` | float | Fraction of current reference-core bond edges recovered. |
| `envelope_core_node_containment` | float | Fraction of current reference-core nodes recovered. |
| `edge_type_6_6_fraction` | float | Fraction of selected represented edges marked `6_6`. |
| `edge_type_5_6_fraction` | float | Fraction of selected represented edges marked `5_6`. |
| `bond_edge_fraction` | float | Fraction of selected edges that are original C60 bond edges. |
| `nonbond_edge_fraction` | float | Fraction of selected edges that are nonbond all-pairs edges. |
| `mean_graph_distance_selected` | float | Mean C60 shortest-path distance of selected edges. |
| `connected_component_count` | float | Connected component count in selected envelope. |

---

## 6. Real-vs-null summary

Output:

```text
bms_fu01c_real_vs_null_summary.csv
```

| field name | type | description |
|---|---:|---|
| `representation_id` | string | Representation label. |
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

## 7. Representation summary

Output:

```text
bms_fu01c_representation_summary.csv
```

| field name | type | description |
|---|---:|---|
| `representation_id` | string | Representation label. |
| `null_family` | string | Null family label. |
| `summary_row_count` | integer | Number of summary rows. |
| `label_counts` | JSON string | Counts by interpretation label. |
| `core_metric_real_exceeds_count` | integer | Core-metric rows labeled real-exceeds. |
| `core_metric_null_reproduces_count` | integer | Core-metric rows labeled null-reproduces-core. |

---

## 8. Core variant summary

Output:

```text
bms_fu01c_core_variant_summary.csv
```

| field name | type | description |
|---|---:|---|
| `representation_id` | string | Representation label. |
| `core_variant_id` | string | Core variant label. |
| `null_family` | string | Null family label. |
| `summary_row_count` | integer | Number of summary rows. |
| `label_counts` | JSON string | Counts by interpretation label. |
| `core_metric_real_exceeds_count` | integer | Core-metric rows labeled real-exceeds. |
| `core_metric_null_reproduces_count` | integer | Core-metric rows labeled null-reproduces-core. |

---

## 9. Null families

| field name | type | description |
|---|---:|---|
| `degree_preserving_rewire` | null family | Preserves degree sequence while perturbing topology and shuffling edge-type counts. |
| `edge_class_shuffle` | null family | Preserves topology and edge-type counts but shuffles edge-class placement. |
| `motif_class_preserving_edge_swap_proxy` | null family | Rewires only within the same edge-type class. Proxy only; does not preserve true fullerene faces. |
| `core_seeded_decoy` | null family | Forces current reference-core edges to target edge type while preserving counts. |

---

## 10. Interpretation boundary

Allowed:

```text
BMS-FU01c tests whether C60 signal is carried by edge-class weights, topology-only
connectivity, or graph-distance relational structure.
```

Not allowed:

```text
C60 proves emergent spacetime.
The bridge recognizes molecules.
A physical metric has been recovered.
Global C60 symmetry has been fully recovered.
Quantum chemistry has been reproduced.
```
