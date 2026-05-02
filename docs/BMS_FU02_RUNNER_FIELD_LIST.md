# BMS-FU02 — Runner Field List

Date: 2026-05-01  
Project: Gravitation und RaumZeit / Quantum-Spacetime-Bridge  
Recommended repo target: `docs/BMS_FU02_RUNNER_FIELD_LIST.md`  
Status: Companion field list for BMS-FU02 load-bearing pattern analysis

---

## 1. Purpose

BMS-FU02 analyzes which C60 edges, nodes and motifs act as candidate load-bearing relational patterns in the FU01c diagnostic outputs.

Working question:

```text
Welche Muster tragen — und warum tragen sie?
```

---

## 2. Config fields

| field name | type | description |
|---|---:|---|
| `run.run_id` | string | Stable run identifier. |
| `run.output_dir` | string | Output directory. |
| `run.random_seed` | integer | Seed placeholder; FU02-v0 is deterministic. |
| `inputs.fu01c_output_dir` | string | FU01c output directory. |
| `inputs.c60_nodes_csv` | string | Validated C60 nodes. |
| `inputs.c60_edges_csv` | string | Validated C60 bond edges. |
| `inputs.c60_faces_csv` | string | Validated C60 faces. |
| `inputs.c60_graph_manifest_json` | string | C60 graph validation manifest. |
| `selection.include_construction_families` | list[string] | FU01c construction families considered for pattern reconstruction. |
| `selection.positive_delta_threshold` | float | Minimum positive real-over-null delta for persistence count. |
| `selection.strong_delta_threshold` | float | Threshold for strong-context count. |
| `selection.cross_representation_min_count` | integer | Minimum representation count for cross-representation carrier logic. |
| `labels.topology_sensitive_representations` | list[string] | Representations treated as topology-sensitive. |
| `labels.null_families` | list[string] | Null family labels expected from FU01c. |

---

## 3. Edge explanatory features

Output:

```text
bms_fu02_edge_explanatory_features.csv
```

| field name | type | description |
|---|---:|---|
| `edge_key` | string | Canonical edge id `source--target`. |
| `source` | string | Source node id. |
| `target` | string | Target node id. |
| `edge_type` | string | C60 edge class: `6_6` or `5_6`. |
| `shared_faces` | string | Incident face ids. |
| `shared_face_types` | string | Incident face type signature, e.g. `H,H` or `H,P`. |
| `pentagon_incident` | bool | Whether edge touches at least one pentagon. |
| `hexagon_hexagon_edge` | bool | Whether edge is a 6:6 H-H edge. |
| `local_face_signature` | string | Compact motif signature. |
| `cycle5_proxy_count` | integer | Number of incident pentagon face entries. |
| `cycle6_proxy_count` | integer | Number of incident hexagon face entries. |
| `line_graph_degree` | integer | Number of adjacent C60 bond edges sharing one endpoint. |
| `edge_betweenness_proxy` | float | Simple shortest-path edge-betweenness proxy. |
| `mean_endpoint_shortest_path_centrality` | float | Mean endpoint closeness-like centrality proxy. |
| `endpoint_shell_signature` | string | Endpoint shell placement from `c60_001`. |

---

## 4. Node explanatory features

Output:

```text
bms_fu02_node_explanatory_features.csv
```

| field name | type | description |
|---|---:|---|
| `node_id` | string | C60 node id. |
| `degree` | integer | C60 graph degree; expected 3. |
| `incident_6_6_count` | integer | Number of incident 6:6 edges. |
| `incident_5_6_count` | integer | Number of incident 5:6 edges. |
| `pentagon_membership_count` | integer | Number of incident pentagon faces. |
| `hexagon_membership_count` | integer | Number of incident hexagon faces. |
| `shortest_path_closeness_proxy` | float | Closeness-like centrality proxy. |
| `shell_signature` | string | Distance shell from anchor `c60_001`. |
| `retained_edge_incidence_count` | integer | Number of candidate carrier edges incident to this node. |

---

## 5. Edge load-bearing scores

Output:

```text
bms_fu02_edge_load_bearing_scores.csv
```

Includes explanatory edge fields plus score fields:

| field name | type | description |
|---|---:|---|
| `real_retention_rate` | float | Fraction of real reconstruction contexts retaining this bond edge. |
| `mean_null_retention_rate` | float | Mean null retention rate across null families. |
| `load_bearing_score` | float | Real retention rate minus mean null retention rate. |
| `positive_representation_count` | integer | Number of representations with positive real-over-null delta. |
| `positive_representations` | string | Semicolon-separated positive representation labels. |
| `positive_topology_representation_count` | integer | Positive count among topology-sensitive representations. |
| `positive_topology_representations` | string | Semicolon-separated topology-sensitive positive representations. |
| `positive_core_variant_count` | integer | Number of core variants with positive deltas. |
| `positive_core_variants` | string | Semicolon-separated positive core variants. |
| `strong_context_count` | integer | Number of contexts with delta >= strong threshold. |
| `null_retention_rates_json` | JSON string | Mean retention rates by null family. |
| `candidate_label` | string | Conservative candidate label. |

---

## 6. Node load-bearing scores

Output:

```text
bms_fu02_node_load_bearing_scores.csv
```

Includes explanatory node fields plus analogous score fields:

| field name | type | description |
|---|---:|---|
| `real_retention_rate` | float | Fraction of real reconstruction contexts retaining incident edge signal. |
| `mean_null_retention_rate` | float | Mean null retention rate. |
| `load_bearing_score` | float | Real retention rate minus mean null retention rate. |
| `positive_representation_count` | integer | Number of representations with positive delta. |
| `positive_representations` | string | Positive representations. |
| `positive_topology_representation_count` | integer | Positive topology-sensitive representation count. |
| `positive_topology_representations` | string | Positive topology-sensitive representations. |
| `positive_core_variant_count` | integer | Number of core variants with positive deltas. |
| `positive_core_variants` | string | Positive core variant labels. |
| `strong_context_count` | integer | Number of strong contexts. |
| `null_retention_rates_json` | JSON string | Mean null retention rates. |
| `candidate_label` | string | Conservative node candidate label. |

---

## 7. Null resistance profiles

Output:

```text
bms_fu02_null_resistance_profiles.csv
```

| field name | type | description |
|---|---:|---|
| `edge_key` | string | Canonical edge id. |
| `<null_family>_mean_delta` | float | Mean real-minus-null retention delta for that null family. |
| `<null_family>_positive_fraction` | float | Fraction of contexts with positive delta for that null family. |

---

## 8. Candidate carriers

Outputs:

```text
bms_fu02_cross_representation_carriers.csv
bms_fu02_candidate_structure_carriers.csv
```

Fields match edge score fields and list edges with positive candidate labels.

Candidate labels:

| field name | type | description |
|---|---:|---|
| `cross_representation_structure_carrier` | label | Positive topology-sensitive persistence in at least two representations and not fully decoy-driven. |
| `topology_only_structure_carrier` | label | Positive in topology-only and graph-distance representations. |
| `weighted_or_mixed_candidate` | label | Positive but not cleanly topology-only. |
| `decoy_reproducible_candidate` | label | Behavior largely reproduced by core-seeded decoy. |
| `motif_proxy_reproducible_candidate` | label | Behavior largely reproduced by motif proxy. |
| `inconclusive_or_tie_sensitive` | label | Weak, zero or construction-sensitive result. |

---

## 9. Motif load-bearing summary

Output:

```text
bms_fu02_motif_load_bearing_summary.csv
```

| field name | type | description |
|---|---:|---|
| `motif_signature` | string | Face/motif signature, e.g. `H,H` or `H,P`. |
| `edge_count` | integer | Number of edges in this motif group. |
| `mean_load_bearing_score` | float | Mean edge load-bearing score in this motif group. |
| `max_load_bearing_score` | float | Maximum edge load-bearing score in this motif group. |
| `candidate_label_counts` | JSON string | Candidate labels counted within motif group. |
| `top_edges` | string | Top edge keys by load-bearing score. |

---

## 10. Interpretation boundary

Allowed:

```text
BMS-FU02 identifies candidate relational structure carriers in the controlled
C60 diagnostic outputs.
```

Not allowed:

```text
The identified carriers are physical spacetime atoms.
C60 proves emergent spacetime.
A physical metric has been recovered.
Global C60 symmetry has been fully recovered.
```
