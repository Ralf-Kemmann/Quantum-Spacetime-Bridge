# BMS-ST01 — Runner Field List

Date: 2026-05-01  
Project: Gravitation und RaumZeit / Quantum-Spacetime-Bridge  
Recommended repo target: `docs/BMS_ST01_RUNNER_FIELD_LIST.md`  
Status: Companion field list for BMS-ST01 structure-information diagnostic

---

## 1. Purpose

BMS-ST01 applies BMC-15h-style structured-specificity diagnostics to a prebuilt relational structure graph.

Input graph:

```text
data/baseline_relational_table_real.csv
```

Node metadata:

```text
data/node_metadata_real.csv
```

The test asks whether structure-family information is expressed as local relational edge organization beyond coarse family labels and cheap seeded cores.

---

## 2. Config fields

### `run`

| field name | type | description |
|---|---:|---|
| `run.run_id` | string | Stable run identifier. |
| `run.output_dir` | string | Output directory for the run. |
| `run.random_seed` | integer | Seed for null generation. |

### `inputs`

| field name | type | description |
|---|---:|---|
| `inputs.edge_table` | string | Path to real relational edge table. |
| `inputs.node_metadata` | string | Path to node metadata table. |
| `inputs.dataset_manifest` | string | Path to dataset manifest, used for provenance. |

### `reference_core`

| field name | type | description |
|---|---:|---|
| `reference_core.mode` | string | Reference-core mode; default `family_balanced_within_family_top_edges`. |
| `reference_core.edges_per_family` | integer | Number of top within-family edges selected per structure family. |
| `reference_core.within_family_only` | boolean | Whether reference core is limited to within-family edges. |
| `reference_core.families` | list[string] | Families to include in the balanced core. |

---

## 3. Node output table

Output:

```text
bms_st01_nodes_resolved.csv
```

| field name | type | description |
|---|---:|---|
| `node_id` | string | Unique structure node id. |
| `shell_index` | integer-like string | Family/shell index from metadata. |
| `node_label` | string | Human-readable node label. |
| `node_family` | string | Structure family label, e.g. `RING`, `CAVITY`, `MEMBRANE`. |
| `origin_tag` | string | Source/construction origin tag. |
| `comment` | string | Node-level methodological note. |
| `feature_shape_factor` | numeric-like string | Shape-factor feature. |
| `feature_spectral_index` | numeric-like string | Spectral-index feature. |

---

## 4. Edge output table

Output:

```text
bms_st01_edges.csv
```

| field name | type | description |
|---|---:|---|
| `object_id` | string | Graph object id: `real` or null object. |
| `null_family` | string | Null family label or `real`. |
| `repeat_index` | integer/string | Repeat index or `real`. |
| `source` | string | Source node id. |
| `target` | string | Target node id. |
| `weight` | float | Edge similarity weight. |
| `distance` | float | Derived distance proxy `1 / weight - 1`. |
| `edge_family` | string | Original edge family where available. |
| `source_family` | string | Original source family where available. |
| `target_family` | string | Original target family where available. |
| `relation_type` | string | Relation type or null assignment tag. |
| `evidence_tag` | string | Source evidence tag. |
| `comment` | string | Edge-level comment. |

---

## 5. Reference core table

Output:

```text
bms_st01_reference_core_edges.csv
```

| field name | type | description |
|---|---:|---|
| `family_id` | string | Family for which the reference-core edge was selected. |
| `source` | string | Source node id. |
| `target` | string | Target node id. |
| `weight` | float | Real edge weight. |
| `reference_core_rule` | string | Reference-core rule. |
| `source_family` | string | Source node family. |
| `target_family` | string | Target node family. |
| `source_label` | string | Source node label. |
| `target_label` | string | Target node label. |
| `source_shape_factor` | numeric-like string | Source shape factor. |
| `target_shape_factor` | numeric-like string | Target shape factor. |
| `source_spectral_index` | numeric-like string | Source spectral index. |
| `target_spectral_index` | numeric-like string | Target spectral index. |

---

## 6. Metric tables

Outputs:

```text
bms_st01_core_metrics.csv
bms_st01_envelope_metrics.csv
```

| field name | type | description |
|---|---:|---|
| `object_id` | string | Graph object id. |
| `null_family` | string | Null family label or `real`. |
| `repeat_index` | integer/string | Repeat index or `real`. |
| `construction_family` | string | Construction family. |
| `construction_variant` | string | Construction variant. |
| `edge_count` | integer | Number of edges in constructed envelope. |
| `node_count` | integer | Number of nodes touched by constructed envelope. |
| `metric_name` | string | Metric name. |
| `metric_value` | float | Metric value. |

Metric names:

| field name | type | description |
|---|---:|---|
| `envelope_core_edge_containment` | float | Fraction of reference-core edges recovered by envelope. |
| `envelope_core_node_containment` | float | Fraction of reference-core nodes recovered by envelope. |
| `family_purity` | float | Fraction of envelope edges with both nodes in the same family. |
| `cross_family_fraction` | float | Fraction of envelope edges crossing structure families. |

---

## 7. Real-vs-null summary

Output:

```text
bms_st01_real_vs_null_summary.csv
```

| field name | type | description |
|---|---:|---|
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

## 8. Interpretation boundary

Allowed:

```text
BMS-ST01 tests whether structure-feature outputs contain local relational
organization beyond coarse family labels.
```

Not allowed:

```text
BMS-ST01 proves emergent spacetime.
The bridge recognizes geometry.
A physical metric has been recovered.
```
