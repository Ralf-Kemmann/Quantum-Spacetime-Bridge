# BMC-15e Preflight — Observed Graph Object Export Note

## Purpose

The BMC-15e runner requires explicit observed graph-object edge lists.

The BMC-15 diagnostic run wrote summary files and JSON references, but did not create a `graph_objects/` directory with per-object edge lists.

This preflight step exports those graph objects without introducing new numerics.

## Input sources

The exporter reads:

```text
runs/BMC-15/geometry_proxy_diagnostics_open/bmc15_metrics.json
```

From this file it uses:

```text
edge_inventory_csv
backbone_edges_csv
graphs
```

Current referenced source files:

```text
runs/BMC-12e/edgecount_neighborhood_sweep_open/bmc12e_edgecount_sweep_edges_inventory.csv
runs/BMC-13/alternative_backbone_consensus_open/bmc13_backbone_edges.csv
```

## Exported graph objects

The expected BMC-15 graph list is:

```text
N81_full_baseline
top_strength_reference_core
maximum_spanning_tree_envelope
mutual_kNN_k3_envelope
threshold_path_consensus_envelope
```

The exporter writes:

```text
runs/BMC-15/geometry_proxy_diagnostics_open/graph_objects/
  N81_full_baseline_edges.csv
  top_strength_reference_core_edges.csv
  maximum_spanning_tree_envelope_edges.csv
  mutual_kNN_k3_envelope_edges.csv
  threshold_path_consensus_envelope_edges.csv
```

Each edge list has columns:

```text
source
target
weight
distance
source_graph
source_file
export_rule
```

## Export rules

### `N81_full_baseline`

Source:

```text
edge_inventory_csv
```

Filter:

```text
edge_count_target = 81
case_id = baseline_all_features
```

### Backbone/envelope objects

Source:

```text
backbone_edges_csv
```

Mapping:

```text
top_strength_reference_core        -> method_id = top_strength_reference
maximum_spanning_tree_envelope     -> method_id = maximum_spanning_tree
mutual_kNN_k3_envelope             -> method_id = mutual_kNN_k3
threshold_path_consensus_envelope  -> method_id = threshold_path_consensus
```

Additional filters:

```text
edge_count_target = 81
case_id = baseline_all_features
selected_by_method = True
```

## Methodological boundary

This exporter does not recompute the BMC-15 diagnostics.

It does not create new graph definitions.

It only materializes the graph objects already referenced by the BMC-15 metrics file into explicit edge-list CSV files required by BMC-15e.

## Recommended workflow

```bash
cd ~/Downloads/deBroglie_Kaster_Theorie/quantum-spacetime-bridge

python3 scripts/export_bmc15_observed_graph_objects.py --dry-run

python3 scripts/export_bmc15_observed_graph_objects.py

python3 scripts/run_bmc15e_geometry_control_nulls.py \
  --config data/bmc15e_geometry_control_nulls_config.yaml
```

## Field list

| Field name | Field type | Description |
|---|---|---|
| `source` | string | Source node ID. |
| `target` | string | Target node ID. |
| `weight` | float | Edge weight copied from the referenced source CSV. |
| `distance` | float/null | Edge distance if available in source, otherwise empty. |
| `source_graph` | string | BMC-15 graph object name being exported. |
| `source_file` | path/string | Source CSV used for this export. |
| `export_rule` | string | Filter/mapping rule used to produce the edge list. |
