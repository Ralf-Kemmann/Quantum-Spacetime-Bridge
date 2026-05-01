# BMS-IS01b — Runner Field List

Date: 2026-05-01  
Project: Gravitation und RaumZeit / Quantum-Spacetime-Bridge  
Recommended repo target: `docs/BMS_IS01B_RUNNER_FIELD_LIST.md`  
Status: Companion field list for BMS-IS01b family-balanced diagnostic

---

## 1. Purpose

BMS-IS01b refines BMS-IS01 by using a family-balanced reference core and by optionally excluding same-isotope cross-run edges from the reference-core definition.

The diagnostic asks whether isotope-family matter-signature graphs contain local relational edge structure beyond the run-stability identity links found in BMS-IS01.

---

## 2. Config fields

### `run`

| field name | type | description |
|---|---:|---|
| `run.run_id` | string | Stable run identifier. |
| `run.output_dir` | string | Output directory for the run. |
| `run.random_seed` | integer | Seed for null generation. |

### `inputs.scan_tables`

| field name | type | description |
|---|---:|---|
| `run_id` | string | Source run label. |
| `family_id` | string | Isotope family label. |
| `test_axis` | string | Test axis label. |
| `source_path` | string | Source scan CSV path. |
| `delta_column` | string | Family-specific delta column mapped to canonical `matter_sensitive_delta`. |

### `reference_core`

| field name | type | description |
|---|---:|---|
| `mode` | string | Reference-core mode; for BMS-IS01b use `family_balanced_top_edges`. |
| `edges_per_family` | integer | Number of reference-core edges selected per family. |
| `exclude_same_isotope_cross_run` | boolean | Whether same-isotope cross-run edges are excluded from reference-core selection. |
| `fallback_allow_same_isotope_if_needed` | boolean | Whether excluded same-isotope edges may be used if too few eligible edges exist. |

---

## 3. Node table

Output:

```text
bms_is01b_nodes_resolved.csv
```

| field name | type | description |
|---|---:|---|
| `node_id` | string | Unique node id: family, run, and isotope. |
| `run_id` | string | Source run id. |
| `family_id` | string | Family label. |
| `test_axis` | string | Test axis label. |
| `isotope` | string | Isotope id. |
| `label` | string | Human-readable isotope label. |
| `element_symbol` | string | Element symbol. |
| `mass_u` | float-like string | Isotope mass. |
| `proton_number` | integer-like string | Proton number. |
| `neutron_number` | integer-like string | Neutron number. |
| `electron_count` | integer-like string | Electron count. |
| `lambda_db` | float-like string | de Broglie wavelength proxy. |
| `energy_j` | float-like string | Energy proxy. |
| `number_density` | float-like string | Number-density proxy. |
| `valence_electron_count` | integer-like string | Valence electron count. |
| `shell_closure_score` | float-like string | Shell closure score. |
| `length_scale_score` | float-like string | Length-scale score. |
| `energy_score` | float-like string | Energy score. |
| `occupancy_score` | float-like string | Occupancy score. |
| `signature_score_wave` | float-like string | Wave signature score. |
| `valence_score` | float-like string | Valence score. |
| `signature_score_combined` | float-like string | Combined signature score. |
| `matter_sensitive_delta` | float-like string | Canonical delta mapped from source delta column. |
| `source_delta_column` | string | Original source delta column. |
| `source_file` | string | Original source CSV path. |

---

## 4. Reference core table

Output:

```text
bms_is01b_reference_core_edges.csv
```

| field name | type | description |
|---|---:|---|
| `family_id` | string | Family from which the edge was selected. |
| `source` | string | Source node id. |
| `target` | string | Target node id. |
| `weight` | float | Real graph edge weight. |
| `reference_core_rule` | string | Reference-core rule. |
| `excluded_same_isotope_cross_run` | boolean | Whether the edge matched the same-isotope cross-run exclusion rule. Selected strict-core rows should be false. |
| `fallback_selected_same_isotope_cross_run` | boolean | Whether an excluded edge was selected by fallback. |
| `source_isotope` | string | Source isotope id. |
| `target_isotope` | string | Target isotope id. |
| `source_run_id` | string | Source run id. |
| `target_run_id` | string | Target run id. |

---

## 5. Edge table

Output:

```text
bms_is01b_edges.csv
```

| field name | type | description |
|---|---:|---|
| `object_id` | string | Real or null object id. |
| `null_family` | string | Null family label or `real`. |
| `repeat_index` | integer/string | Repeat index or `real`. |
| `source` | string | Source node id. |
| `target` | string | Target node id. |
| `weight` | float | Similarity weight computed as `exp(-euclidean_distance)`. |
| `distance` | float | Euclidean distance on normalized signature vector. |

---

## 6. Metric tables

Outputs:

```text
bms_is01b_core_metrics.csv
bms_is01b_envelope_metrics.csv
```

| field name | type | description |
|---|---:|---|
| `object_id` | string | Real or null object id. |
| `null_family` | string | Null family label or `real`. |
| `repeat_index` | integer/string | Repeat index or `real`. |
| `construction_family` | string | Construction family. |
| `construction_variant` | string | Construction variant. |
| `edge_count` | integer | Constructed envelope edge count. |
| `node_count` | integer | Constructed envelope node count. |
| `metric_name` | string | Metric name. |
| `metric_value` | float | Metric value. |

Metric names:

| field name | type | description |
|---|---:|---|
| `envelope_core_edge_containment` | float | Fraction of reference-core edges recovered by envelope. |
| `envelope_core_node_containment` | float | Fraction of reference-core nodes recovered by envelope. |
| `family_purity` | float | Fraction of envelope edges within the same `family_id`. |

---

## 7. Summary table

Output:

```text
bms_is01b_real_vs_null_summary.csv
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
| `real_minus_null_mean` | float | Difference between real and null mean. |
| `empirical_exceedance_fraction` | float | Fraction of null repeats with value greater than or equal to real. |
| `null_count` | integer | Number of null repeats summarized. |
| `interpretation_label` | string | Conservative interpretation label. |

---

## 8. Interpretation boundary

Allowed:

```text
BMS-IS01b tests whether family-balanced isotope signature cores remain
informative after excluding same-isotope cross-run links.
```

Not allowed:

```text
BMS-IS01b proves physical geometry.
The bridge recognizes isotopes.
Matter identity is transferred to geometry.
```
