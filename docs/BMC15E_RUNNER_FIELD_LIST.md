# BMC-15e Runner Field List

This companion note documents the runner-facing fields used by:

```text
scripts/run_bmc15e_geometry_control_nulls.py
data/bmc15e_geometry_control_nulls_config.yaml
```

## Config fields

| Field name | Field type | Description |
|---|---|---|
| `run_id` | string | Stable identifier for the BMC-15e run. |
| `input.observed_metrics_path` | path/string | Optional path to observed BMC-15 metrics. The runner currently recomputes observed diagnostics for same-code comparison. |
| `input.observed_graphs_dir` | path/string | Directory containing observed graph-object edge lists. |
| `output.output_dir` | path/string | Output directory for BMC-15e run artifacts. |
| `random.seed` | integer | Seed for reproducible control generation. |
| `random.n_replicates` | integer | Number of geometry-control replicates per object/family/dimension/weight mode. |
| `random.max_generation_attempts` | integer | Maximum attempts to satisfy connectedness preference for generated controls. |
| `graph_objects` | list[string] | Observed graph objects to load from `input.observed_graphs_dir`. |
| `control_families` | list[mapping] | Geometry-control families to generate. |
| `control_families.name` | string | Control family name. Supported MVP values: `soft_geometric_kernel`, `random_geometric_graph`. |
| `control_families.enabled` | boolean | Whether this family is active. |
| `control_families.dimensions` | list[integer] | Latent geometry dimensions to test. |
| `control_families.matching.node_count` | string | Matching mode for node count. MVP assumes exact observed node count. |
| `control_families.matching.edge_count` | string | Matching mode for edge count. MVP assumes exact observed edge count. |
| `control_families.matching.connected` | string | `prefer_true` tries to generate connected controls within max attempts. |
| `control_families.weight_modes` | list[string] | Supported MVP values: `unweighted`, `observed_rank_remap`. |
| `control_families.generator_params` | mapping | Family-specific generator parameters. |
| `diagnostics` | mapping | Boolean switches retained for documentation; MVP computes the implemented diagnostics. |
| `embedding.dimensions` | list[integer] | Embedding dimensions used for normalized stress, typically `[2, 3, 4]`. |
| `embedding.distance_mode` | string | Distance mode label. MVP uses shortest-path distances. |
| `embedding.disconnected_policy` | string | Policy for disconnected graphs. MVP supports `largest_component`. |
| `labeling.tie_tolerance` | float | Numerical tolerance for equality/ties. |
| `labeling.all_zero_tie_label` | string | Label used when observed and control distribution are all zero. |
| `labeling.directional_metrics` | mapping | Metric-specific direction of more/less geometry-like interpretation. |
| `readout` | mapping | Boolean output switches retained for documentation. |

## Output fields: `geometry_control_metrics.csv`

| Field name | Field type | Description |
|---|---|---|
| `run_id` | string | Run identifier copied from config. |
| `observed_object` | string | Observed graph object used as size/edge reference. |
| `control_family` | string | Generated control family. |
| `dimension` | integer | Latent geometry dimension used to generate the control. |
| `weight_mode` | string | Control weight mode. |
| `replicate` | integer | Replicate index. |
| `replicate_seed` | integer | Seed used for this replicate. |
| `generation_attempts` | integer | Number of attempts used to satisfy connectedness preference. |
| `connected_after_generation` | boolean | Whether generated control was connected. |
| `n_nodes` | integer | Number of graph nodes. |
| `n_edges` | integer | Number of graph edges. |
| `n_components` | integer | Number of connected components. |
| `is_connected` | boolean | Whether the graph is connected. |
| `avg_degree` | float | Average graph degree. |
| `degree_std` | float | Standard deviation of graph degree. |
| `degree_max` | float | Maximum graph degree. |
| `density` | float | NetworkX graph density. |
| `distance_node_count` | integer | Node count used in distance-matrix diagnostics after disconnected-policy handling. |
| `distance_policy` | string | Distance policy actually used. |
| `triangle_defects` | integer | Count of direct triangle inequality defects in shortest-path distance matrix. |
| `negative_eigenvalue_burden` | float | Fractional burden of negative eigenvalues after classical MDS double-centering. |
| `negative_eigenvalue_count` | integer | Number of negative eigenvalues below tolerance. |
| `geodesic_consistency_error` | float | Coefficient-of-variation proxy for finite geodesic distances. |
| `local_dimension_proxy` | float | Very cautious graph-distance dimension-like proxy; not a physical dimension. |
| `embedding_stress_2d` | float | Normalized MDS stress in 2D, if scikit-learn is available. |
| `embedding_stress_3d` | float | Normalized MDS stress in 3D, if scikit-learn is available. |
| `embedding_stress_4d` | float | Normalized MDS stress in 4D, if scikit-learn is available. |

## Output fields: `observed_position_summary.csv`

| Field name | Field type | Description |
|---|---|---|
| `observed_object` | string | Observed graph object. |
| `control_family` | string | Control family compared against. |
| `dimension` | integer | Control latent dimension. |
| `weight_mode` | string | Control weight mode. |
| `metric` | string | Metric being compared. |
| `observed_value` | float | Observed value recomputed by this runner. |
| `control_min` | float | Minimum control value. |
| `control_median` | float | Median control value. |
| `control_max` | float | Maximum control value. |
| `control_n` | integer | Number of finite control values. |
| `position_label` | string | Defensive observed-vs-control label. |
