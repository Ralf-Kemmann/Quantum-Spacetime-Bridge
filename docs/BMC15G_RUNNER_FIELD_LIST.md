# BMC-15g Runner Field List

## `perturbation_metrics.csv`

- `perturbation_type` — string — perturbation family.
- `strength` — float — perturbation strength parameter.
- `seed` — integer — random seed family.
- `repeat_index` — integer — repeat index.
- `n_nodes` — integer — node count of perturbed graph.
- `n_edges` — integer — edge count of perturbed graph.
- `n_components` — integer — number of connected components.
- `is_connected` — boolean — true if graph has one connected component.
- `avg_degree` — float — average graph degree.
- `degree_std` — float — degree standard deviation.
- `degree_max` — float — maximum graph degree.
- `density` — float — graph density.
- `reference_core_edges` — integer — number of reference core edges.
- `candidate_core_edges` — integer — number of reconstructed candidate-core edges.
- `core_edge_intersection` — integer — shared edges between candidate core and reference core.
- `core_edge_retention_fraction` — float — shared/reference-core edge fraction.
- `core_edge_jaccard` — float — edge Jaccard index between candidate and reference core.
- `reference_core_nodes` — integer — number of nodes touched by the reference core.
- `candidate_core_nodes` — integer — number of nodes touched by the candidate core.
- `core_node_intersection` — integer — shared nodes between candidate and reference core.
- `core_node_retention_fraction` — float — shared/reference-core node fraction.
- `containment_label` — string — descriptive retention bin.

## `envelope_overlap_summary.csv`

- `perturbation_type` — string — perturbation family.
- `strength` — float — perturbation strength parameter.
- `seed` — integer — random seed family.
- `repeat_index` — integer — repeat index.
- `reference_name` — string — reference envelope name.
- `reference_edges` — integer — reference envelope edge count.
- `candidate_edges` — integer — candidate envelope edge count.
- `edge_intersection` — integer — shared edges between candidate and reference envelope.
- `edge_retention_fraction` — float — shared/reference edge fraction.
- `edge_jaccard` — float — envelope edge Jaccard index.

## `family_summary.csv`

- `perturbation_type` — string — perturbation family.
- `strength` — float — perturbation strength parameter.
- `n` — integer — number of perturbation repeats in the group.
- `core_edge_retention_fraction_mean` — float — mean reference-core edge retention.
- `core_edge_retention_fraction_min` — float — minimum reference-core edge retention.
- `core_edge_retention_fraction_max` — float — maximum reference-core edge retention.
- `core_edge_jaccard_mean` — float — mean candidate/reference-core edge Jaccard.
- `core_node_retention_fraction_mean` — float — mean reference-core node retention.
- `connected_fraction` — float — fraction of runs with connected perturbed graph.
