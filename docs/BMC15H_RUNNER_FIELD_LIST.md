# BMC-15h Runner Field List

Date: 2026-05-01  
Project: Gravitation und RaumZeit / Quantum-Spacetime-Bridge  
Companion script: `scripts/run_bmc15h_structured_specificity_extension.py`  
Companion config: `data/bmc15h_structured_specificity_extension_config.yaml`

---

## 1. Purpose

This document lists the expected output fields for the BMC-15h structured
specificity diagnostic.

BMC-15h asks whether structured null families reproduce the same compact-core
and envelope behavior seen in the BMC-15e/f/g line.

The runner output is diagnostic and construction-qualified. It must not be read
as a proof of physical spacetime, unique geometry, metric recovery, causal
structure, Lorentzian structure, continuum limit, or specificity.

---

## 2. Output files

Default output directory:

```text
runs/BMC-15h/structured_specificity_extension_open/
```

Default files:

```text
bmc15h_core_metrics.csv
bmc15h_envelope_metrics.csv
bmc15h_real_vs_null_summary.csv
bmc15h_null_family_inventory.csv
bmc15h_run_manifest.json
bmc15h_warnings.json
bmc15h_config_resolved.yaml
```

---

## 3. `bmc15h_core_metrics.csv`

| Field name | Type | Description |
|---|---:|---|
| run_id | string | Unique identifier for the BMC-15h run. |
| object_role | string | Object role: `real` for the canonical graph or `null` for a structured control object. |
| null_family | string | Null family label. Uses `canonical` for the real object. |
| null_repeat | integer/null | Repeat index for null objects; null for the real object. |
| seed | integer/null | Random seed used for the null repeat or perturbation; null for deterministic real rows. |
| construction_family | string | Envelope or graph construction family, e.g. `top_strength`, `threshold`, `mutual_knn`, `maximum_spanning_tree`. |
| construction_variant | string | Concrete construction variant, e.g. `top_edges_21`, `k_4`, `abs_weight_ge_0.03`. |
| perturbation_family | string/null | Perturbation family if a later extension adds perturbations; null in the initial BMC-15h runner. |
| perturbation_strength | float/null | Perturbation strength if a later extension adds perturbations; null in the initial BMC-15h runner. |
| core_edge_retention | float | Fraction of reference-core edges retained inside the constructed envelope or graph object. |
| core_node_retention | float | Fraction of reference-core nodes represented by retained reference-core edges. |
| core_connected | boolean | Whether the retained/reconstructed core subgraph is connected. |
| core_component_count | integer | Number of connected components in the retained/reconstructed core subgraph. |
| core_largest_component_fraction | float | Fraction of retained/reconstructed core nodes contained in the largest component. |
| core_mean_weight | float/null | Mean weight of retained/reconstructed core edges when available in the current graph object. |
| core_weight_rank_stability | float/null | Placeholder for later rank-stability diagnostics; null in the initial implementation. |
| warning_count | integer | Number of warnings recorded globally at the time this row was generated. |

---

## 4. `bmc15h_envelope_metrics.csv`

| Field name | Type | Description |
|---|---:|---|
| run_id | string | Unique identifier for the BMC-15h run. |
| object_role | string | Object role: `real` or `null`. |
| null_family | string | Null family label. Uses `canonical` for the real object. |
| null_repeat | integer/null | Repeat index for null objects; null for the real object. |
| seed | integer/null | Random seed used for the null repeat; null for deterministic real rows. |
| construction_family | string | Envelope construction family. |
| construction_variant | string | Concrete envelope construction variant. |
| envelope_node_count | integer | Number of nodes represented in the constructed envelope. |
| envelope_edge_count | integer | Number of edges represented in the constructed envelope. |
| envelope_density | float | Undirected graph density of the envelope using represented envelope nodes. |
| envelope_connected | boolean | Whether the envelope is connected. |
| envelope_component_count | integer | Number of connected components in the envelope. |
| envelope_core_edge_containment | float | Fraction of reference-core edges contained in the envelope. |
| envelope_core_node_containment | float | Fraction of reference-core nodes represented by contained reference-core edges. |
| envelope_edge_overlap_to_real | float/null | Count of overlapping edges relative to the matching canonical real envelope. |
| envelope_jaccard_to_real | float/null | Jaccard edge similarity relative to the matching canonical real envelope. |
| warning_count | integer | Number of warnings recorded globally at the time this row was generated. |

---

## 5. `bmc15h_real_vs_null_summary.csv`

| Field name | Type | Description |
|---|---:|---|
| run_id | string | Unique identifier for the BMC-15h run. |
| metric_name | string | Metric being compared between the canonical object and a null family. |
| construction_family | string | Construction family used for the comparison. |
| construction_variant | string | Concrete construction variant used for the comparison. |
| null_family | string | Null family used for the comparison. |
| real_value | float | Metric value for the canonical object. |
| null_mean | float | Mean of the null-family metric values. |
| null_median | float | Median of the null-family metric values. |
| null_std | float | Sample standard deviation of the null-family metric values. |
| null_min | float | Minimum null-family metric value. |
| null_max | float | Maximum null-family metric value. |
| real_minus_null_mean | float | Difference between the canonical value and the null-family mean. |
| real_minus_null_median | float | Difference between the canonical value and the null-family median. |
| empirical_exceedance_fraction | float | Fraction of null values equal to or more extreme than the real value, using the configured comparison direction. |
| real_rank_position | float/integer/null | Rank-like position of the real value among null values; convention depends on comparison direction. |
| n_null_repeats | integer | Number of null repeats entering the comparison. |
| comparison_direction | string | Comparison direction: `higher_is_more_core_like`, `lower_is_more_core_like`, or `two_sided`. |
| interpretation_label | string | Conservative diagnostic label assigned by threshold rule. |

Allowed `interpretation_label` values:

```text
null_reproduces_core_behavior
real_exceeds_tested_null_family
mixed_family_dependent_result
construction_sensitive_result
inconclusive_due_to_warnings_or_scope
```

Current initial runner emits the first, second, third, or inconclusive labels.
`construction_sensitive_result` is reserved for later synthesis logic across
construction families.

---

## 6. `bmc15h_null_family_inventory.csv`

| Field name | Type | Description |
|---|---:|---|
| run_id | string | Unique identifier for the BMC-15h run. |
| null_family | string | Null family label. |
| null_repeat | integer | Repeat index within the null family. |
| seed | integer | Random seed used for this null repeat. |
| node_count | integer | Number of nodes in the generated null object. |
| edge_count | integer | Number of edges in the generated null object. |
| density | float | Undirected graph density of the generated null object. |
| connected | boolean | Whether the generated null object is connected. |
| component_count | integer | Number of connected components in the generated null object. |

---

## 7. `bmc15h_run_manifest.json`

| Field name | Type | Description |
|---|---:|---|
| run_id | string | Unique identifier for the run. |
| created_at | string | UTC ISO timestamp of run creation. |
| script_name | string | Runner script name. |
| config_path | string | Path to YAML config used for the run. |
| output_dir | string | Output directory used by the run. |
| input_files | object | Mapping of input roles to resolved local paths. |
| null_families | array[string] | Null families included in the run. |
| construction_families | array[string] | Construction families included in the run. |
| perturbation_families | array[string] | Perturbation families included in the run; empty in the initial runner. |
| seeds | array[integer] | Random seeds used for null objects. |
| repeats_per_family | object | Mapping from null family label to repeat count. |
| row_counts | object | Row counts for all primary outputs. |
| warnings_file | string | Path to the warnings JSON file. |
| notes | string | Conservative run note and limitation statement. |

---

## 8. `bmc15h_warnings.json`

| Field name | Type | Description |
|---|---:|---|
| warning_id | string | Unique warning identifier. |
| severity | string | Severity label: `info`, `warning`, or `error`. |
| object_role | string/null | Associated object role when applicable. |
| null_family | string/null | Associated null family when applicable. |
| null_repeat | integer/null | Associated repeat index when applicable. |
| construction_family | string/null | Associated construction family when applicable. |
| message | string | Human-readable warning message. |
| affected_output | string/null | Output file, optional input, or diagnostic affected by the warning. |

---

## 9. `bmc15h_config_resolved.yaml`

This file stores the resolved configuration used for the run.

It is not a result metric file. It is included to support reproducibility and
later audit of parameter choices.

---

## 10. Interpretation constraints

The following interpretations are allowed:

```text
structured specificity diagnostic
construction-qualified comparison
geometry-proxy compatible behavior
local core proxy robustness
null-family exceedance diagnostic
```

The following interpretations remain disallowed without substantially stronger
evidence:

```text
physical spacetime emergence proven
unique recovered geometry
Lorentzian structure recovered
causal structure recovered
metric recovered
continuum limit established
specificity proven
```

---

## 11. Minimal validation checklist

After a run, inspect:

```bash
ls -lh runs/BMC-15h/structured_specificity_extension_open

python - <<'PY'
import csv, json
from pathlib import Path
root = Path("runs/BMC-15h/structured_specificity_extension_open")
for name in [
    "bmc15h_core_metrics.csv",
    "bmc15h_envelope_metrics.csv",
    "bmc15h_real_vs_null_summary.csv",
    "bmc15h_null_family_inventory.csv",
]:
    with (root / name).open() as f:
        print(name, sum(1 for _ in csv.DictReader(f)))
print(json.loads((root / "bmc15h_run_manifest.json").read_text())["row_counts"])
print("warnings:", len(json.loads((root / "bmc15h_warnings.json").read_text())))
PY
```

Expected for the initial config with two null families, 50 repeats each, and the
default construction variants:

```text
nonzero core metric rows
nonzero envelope metric rows
nonzero summary rows
100 null inventory rows
manifest present
warnings present, preferably only optional-input warnings
```
