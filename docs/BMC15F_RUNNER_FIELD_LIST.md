# BMC-15f Runner Field List

This companion note documents the runner-facing fields used by:

```text
scripts/run_bmc15f_envelope_construction_sensitivity.py
data/bmc15f_envelope_construction_sensitivity_config.yaml
```

## Config fields

| Field name | Field type | Description |
|---|---|---|
| `run_id` | string | Stable identifier for the BMC-15f run. |
| `input.relational_matrix_path` | path/string | Input relational matrix, edge table, or numeric feature table. |
| `input.node_metadata_path` | path/string | Optional node metadata path retained for documentation. |
| `input.reference_graphs_dir` | path/string | Directory containing BMC-15 observed graph-object edge lists. |
| `input.reference_metrics_path` | path/string | Optional reference metrics path retained for documentation. |
| `output.output_dir` | path/string | Output directory for BMC-15f artifacts. |
| `random.seed` | integer | Seed for reproducible MDS random states and any stochastic extensions. |
| `reference_objects` | list[string] | Reference observed graph objects for edge-overlap comparisons. |
| `core_reference.enabled` | boolean | Whether to compute core containment. |
| `core_reference.object_name` | string | Reference core graph object name. |
| `core_reference.use_for_containment_only` | boolean | Marks the core as containment anchor rather than envelope object. |
| `envelope_families` | list[mapping] | Envelope construction families and parameter grids. |
| `envelope_families.name` | string | Family name, e.g. `mutual_kNN_k_sweep`. |
| `envelope_families.enabled` | boolean | Whether this family is active. |
| `envelope_families.construction_mode` | string | Construction mode, e.g. `mutual_kNN`, `top_fraction_threshold`, `spanning_tree`, `path_consensus`. |
| `envelope_families.weight_source` | string | Weight source label. MVP uses similarity from the relational input. |
| `envelope_families.parameters` | mapping | Parameter grid for the construction family. |
| `diagnostics` | mapping | Boolean diagnostic switches retained for documentation. MVP computes implemented diagnostics. |
| `embedding.dimensions` | list[integer] | Embedding dimensions used for normalized stress. |
| `embedding.distance_mode` | string | Distance mode label. MVP uses shortest-path distances. |
| `embedding.disconnected_policy` | string | Disconnected graph handling policy. MVP supports `largest_component`. |
| `stability.reference_family` | string | Reference family label retained for documentation. |
| `stability.metric_tolerance` | float | Tolerance retained for documentation. |
| `stability.connectedness_required` | boolean | Whether connectedness is required for strong interpretation. |
| `stability.dispersion_thresholds.stable_cv_max` | float | Maximum coefficient of variation for stable label. |
| `stability.dispersion_thresholds.moderately_stable_cv_max` | float | Maximum coefficient of variation for moderately stable label. |
| `labeling.directional_metrics` | mapping | Metric direction mapping retained for downstream interpretation. |

## Output fields: `variant_metrics.csv`

| Field name | Field type | Description |
|---|---|---|
| `run_id` | string | Run identifier copied from config. |
| `envelope_family` | string | Envelope construction family. |
| `variant_name` | string | Unique variant name. |
| `variant_parameters_json` | string/JSON | Variant construction parameters. |
| `n_nodes` | integer | Number of graph nodes. |
| `n_edges` | integer | Number of graph edges. |
| `n_components` | integer | Number of connected components. |
| `is_connected` | boolean | Whether variant graph is connected. |
| `avg_degree` | float | Average degree. |
| `degree_std` | float | Degree standard deviation. |
| `degree_max` | float | Maximum degree. |
| `density` | float | Graph density. |
| `distance_node_count` | integer | Node count used in distance diagnostics after disconnected policy. |
| `distance_policy` | string | Distance handling policy actually used. |
| `triangle_defects` | integer | Count of triangle inequality defects. |
| `negative_eigenvalue_burden` | float | Negative eigenvalue burden from classical MDS-style double centering. |
| `negative_eigenvalue_count` | integer | Count of negative eigenvalues below tolerance. |
| `geodesic_consistency_error` | float | Coefficient-of-variation proxy for finite geodesic distances. |
| `local_dimension_proxy` | float | Cautious dimension-like graph proxy; not a physical dimension. |
| `embedding_stress_2d` | float | Normalized MDS stress in 2D. |
| `embedding_stress_3d` | float | Normalized MDS stress in 3D. |
| `embedding_stress_4d` | float | Normalized MDS stress in 4D. |

## Output fields: `edge_overlap_summary.csv`

| Field name | Field type | Description |
|---|---|---|
| `variant_name` | string | Variant graph name. |
| `envelope_family` | string | Envelope construction family. |
| `reference_object` | string | Reference BMC-15 graph object. |
| `reference_edges` | integer | Number of edges in reference graph. |
| `variant_edges` | integer | Number of edges in variant graph. |
| `edge_jaccard` | float | Jaccard overlap between variant and reference edge sets. |

## Output fields: `core_containment_summary.csv`

| Field name | Field type | Description |
|---|---|---|
| `variant_name` | string | Variant graph name. |
| `envelope_family` | string | Envelope construction family. |
| `core_reference` | string | Core reference graph object. |
| `core_edges_total` | integer | Number of edges in the reference core. |
| `core_edges_contained` | integer | Number of core edges contained in the variant. |
| `core_containment_fraction` | float | Fraction of core edges contained in the variant. |

## Claim boundary

BMC-15f tests envelope-construction sensitivity only.

It does not establish physical geometry, causal structure, Lorentzian signature, light-cone structure, continuum structure, or spacetime emergence.
