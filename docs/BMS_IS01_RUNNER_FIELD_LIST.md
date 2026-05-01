# BMS-IS01 — Runner Field List

Date: 2026-05-01  
Project: Gravitation und RaumZeit / Quantum-Spacetime-Bridge  
Recommended repo target: `docs/BMS_IS01_RUNNER_FIELD_LIST.md`  
Status: Companion field list for BMS-IS01 config and runner outputs

---

## 1. Purpose

This document lists the fields used by the BMS-IS01 isotope / structure specificity diagnostic.

The BMS-IS01 runner converts existing matter-signature isotope scan CSVs into a canonical node table, builds a relational signature graph, and applies BMC-15h-style null diagnostics.

---

## 2. Canonical node table

Output file:

```text
runs/BMS-IS01/isotope_structure_specificity_open/bms_is01_nodes_resolved.csv
```

| field name | type | description |
|---|---:|---|
| `node_id` | string | Unique node identifier: family, run, and isotope combined. |
| `run_id` | string | Source run label, e.g. `hydrogen_run_a`. |
| `family_id` | string | Coarse family label, e.g. `hydrogen_isotopes`, `carbon_isotopes`, `strontium_isotopes`. |
| `test_axis` | string | Method axis, e.g. `isotope` or `isotope_structure_proxy`. |
| `isotope` | string | Machine-readable isotope identifier from the source table. |
| `label` | string | Human-readable isotope label, e.g. `1H`, `12C`, `84Sr`. |
| `element_symbol` | string | Element symbol. |
| `mass_u` | float-like string | Isotope mass in atomic mass units from the source table. |
| `proton_number` | integer-like string | Proton number from the source table. |
| `neutron_number` | integer-like string | Neutron number from the source table. |
| `electron_count` | integer-like string | Electron count from the source table. |
| `lambda_db` | float-like string | de Broglie wavelength proxy from the source table. |
| `energy_j` | float-like string | Energy proxy in joules from the source table. |
| `number_density` | float-like string | Number-density proxy from the source table. |
| `valence_electron_count` | integer-like string | Valence electron count from the source table. |
| `shell_closure_score` | float-like string | Shell-closure score from the source table. |
| `length_scale_score` | float-like string | Length-scale component score. |
| `energy_score` | float-like string | Energy component score. |
| `occupancy_score` | float-like string | Occupancy component score. |
| `signature_score_wave` | float-like string | Wave-side combined signature score. |
| `valence_score` | float-like string | Valence component score. |
| `signature_score_combined` | float-like string | Combined signature score from source run. |
| `matter_sensitive_delta` | float-like string | Normalized delta column mapped from the family-specific source delta column. |
| `source_delta_column` | string | Original source delta column name. |
| `source_file` | string | Source CSV path. |

---

## 3. Edge table

Output file:

```text
bms_is01_edges.csv
```

| field name | type | description |
|---|---:|---|
| `object_id` | string | Graph object identifier: `real` or generated null object. |
| `null_family` | string | Null family label, or `real`. |
| `repeat_index` | integer/string | Null repeat index, or `real` for canonical graph. |
| `source` | string | Source node id. |
| `target` | string | Target node id. |
| `weight` | float | Similarity weight, computed as `exp(-euclidean_distance)` on normalized signature vectors. |
| `distance` | float | Euclidean distance on normalized signature vectors. |

---

## 4. Reference core edge table

Output file:

```text
bms_is01_reference_core_edges.csv
```

| field name | type | description |
|---|---:|---|
| `source` | string | Source node id of reference-core edge. |
| `target` | string | Target node id of reference-core edge. |
| `weight` | float | Real graph similarity weight. |
| `reference_core_rule` | string | Rule used to define the reference core. |

---

## 5. Metric tables

Output files:

```text
bms_is01_core_metrics.csv
bms_is01_envelope_metrics.csv
```

| field name | type | description |
|---|---:|---|
| `object_id` | string | Graph object id. |
| `null_family` | string | Null family label or `real`. |
| `repeat_index` | integer/string | Null repeat index or `real`. |
| `construction_family` | string | Construction family: `top_strength`, `threshold`, `mutual_knn`, or `maximum_spanning_tree`. |
| `construction_variant` | string | Variant label, e.g. `k_2`, `top_edges_10`, `abs_weight_ge_0.8`. |
| `edge_count` | integer | Number of edges in constructed envelope. |
| `node_count` | integer | Number of nodes touched by constructed envelope. |
| `metric_name` | string | Metric name. |
| `metric_value` | float | Metric value. |

Metric names:

| field name | type | description |
|---|---:|---|
| `envelope_core_edge_containment` | float | Fraction of reference-core edges contained in the constructed envelope. |
| `envelope_core_node_containment` | float | Fraction of reference-core nodes contained in the constructed envelope. |
| `family_purity` | float | Fraction of constructed envelope edges connecting nodes from the same `family_id`. |

---

## 6. Real-vs-null summary

Output file:

```text
bms_is01_real_vs_null_summary.csv
```

| field name | type | description |
|---|---:|---|
| `null_family` | string | Null family summarized. |
| `metric_name` | string | Metric summarized. |
| `construction_family` | string | Construction family. |
| `construction_variant` | string | Construction variant. |
| `real_value` | float | Metric value for canonical real graph. |
| `null_mean` | float | Mean metric value across null repeats. |
| `null_min` | float | Minimum metric value across null repeats. |
| `null_max` | float | Maximum metric value across null repeats. |
| `real_minus_null_mean` | float | Difference between real value and null mean. |
| `empirical_exceedance_fraction` | float | Fraction of null repeats with metric value greater than or equal to real value. |
| `null_count` | integer | Number of null samples summarized. |
| `interpretation_label` | string | Conservative interpretation label. |

Interpretation labels:

| field name | type | description |
|---|---:|---|
| `real_exceeds_tested_null_family` | string label | Real value is clearly above tested null family under this readout. |
| `mixed_family_dependent_result` | string label | Null sometimes approaches or exceeds real; result is construction/family dependent. |
| `null_reproduces_core_behavior` | string label | Null family reproduces core-related behavior under this readout. |
| `null_reproduces_metric_behavior` | string label | Null family reproduces a non-core metric such as family purity. |
| `inconclusive_due_to_scope_or_warnings` | string label | Summary could not be interpreted robustly due to missing or invalid values. |

---

## 7. Family summary

Output file:

```text
bms_is01_family_summary.csv
```

| field name | type | description |
|---|---:|---|
| `family_id` | string | Coarse family label. |
| `node_count` | integer | Number of canonical nodes in family. |
| `labels` | string | Semicolon-separated human-readable labels in family. |

---

## 8. Null family inventory

Output file:

```text
bms_is01_null_family_inventory.csv
```

| field name | type | description |
|---|---:|---|
| `object_id` | string | Generated null object id. |
| `null_family` | string | Null family label. |
| `repeat_index` | integer | Repeat index. |

---

## 9. Manifest

Output file:

```text
bms_is01_run_manifest.json
```

| field name | type | description |
|---|---:|---|
| `run_id` | string | Run identifier from config. |
| `output_dir` | string | Output directory from config. |
| `input_table_count` | integer | Number of configured input scan tables. |
| `node_count` | integer | Number of canonical nodes loaded. |
| `real_edge_count` | integer | Number of pairwise real graph edges. |
| `reference_core_edge_count` | integer | Number of reference-core edges. |
| `object_count` | integer | Real plus all null graph objects. |
| `null_family_counts` | object | Number of generated objects per null family. |
| `row_counts` | object | Row counts for generated outputs. |

---

## 10. Warnings

Output file:

```text
bms_is01_warnings.json
```

| field name | type | description |
|---|---:|---|
| `severity` | string | Warning severity, e.g. `warning` or `info`. |
| `message` | string | Human-readable warning message. |

---

## 11. Method boundary

This runner builds a relational diagnostic graph from matter-signature output vectors. It does not claim that the graph is a physical spacetime metric.

Allowed wording:

```text
BMS-IS01 tests whether isotope / structure matter-signature outputs contain
local relational organization beyond simple scalar ordering.
```

Not allowed:

```text
Isotope signatures prove emergent geometry.
The bridge recognizes elements.
A physical metric has been recovered.
```
