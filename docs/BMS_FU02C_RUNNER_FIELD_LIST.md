# BMS-FU02c — Runner Field List

Date: 2026-05-02  
Project: Gravitation und RaumZeit / Quantum-Spacetime-Bridge  
Recommended repo target: `docs/BMS_FU02C_RUNNER_FIELD_LIST.md`

## 1. Purpose

BMS-FU02c recomputes C60 carrier deltas separately for:

```text
bond_class_weighted
topology_only_equal_weight
graph_distance_similarity_d3
```

Working question:

```text
Sind H,H / 6:6 in jeder Brille Lastfäden?
```

## 2. Config fields

| field name | type | description |
|---|---:|---|
| `run.run_id` | string | Stable run identifier. |
| `run.output_dir` | string | Output directory. |
| `inputs.fu01c_output_dir` | string | FU01c output directory. |
| `inputs.c60_edges_csv` | string | Validated C60 edge table. |
| `inputs.c60_nodes_csv` | string | Validated C60 node table. |
| `inputs.c60_faces_csv` | string | Validated C60 face table. |
| `inputs.c60_graph_manifest_json` | string | C60 validation manifest. |
| `selection.include_construction_families` | list[string] | Construction families considered. |
| `selection.reconstruct_graph_distance_shells` | bool | Whether to reconstruct shell contexts; false in v0. |
| `selection.topk_values` | list[integer] | Top-k values for motif enrichment. |
| `representations.expected` | list[string] | Expected representations. |
| `null_families.expected` | list[string] | Expected null families. |

## 3. `bms_fu02c_representation_edge_deltas.csv`

| field name | type | description |
|---|---:|---|
| `representation_id` | string | FU01c representation. |
| `core_variant_id` | string | FU01c core variant. |
| `construction_family` | string | Envelope construction family. |
| `construction_variant` | string | Construction variant. |
| `null_family` | string | Null family. |
| `edge_key` | string | Canonical edge id. |
| `source` | string | Source node. |
| `target` | string | Target node. |
| `edge_type` | string | `6_6` or `5_6`. |
| `shared_face_types` | string | `H,H` or `H,P`. |
| `real_hit` | integer | Whether the real context selected this edge. |
| `null_hit_rate` | float | Mean null selection rate. |
| `delta_edge` | float | `real_hit - null_hit_rate`. |
| `null_object_count` | integer | Null object count. |

## 4. `bms_fu02c_edge_representation_summary.csv`

| field name | type | description |
|---|---:|---|
| `representation_id` | string | Representation id. |
| `edge_key` | string | Canonical edge id. |
| `mean_delta_all_nulls` | float | Mean delta across contexts/nulls. |
| `min_delta_across_nulls` | float | Conservative min/null-penalized delta. |
| `max_delta_across_nulls` | float | Maximum null-family delta. |
| `positive_null_family_count` | integer | Count of null families with positive delta. |
| `null_family_count` | integer | Number of null families. |
| `decoy_penalized_positive` | bool | Whether min delta is positive. |
| `rank_mean_delta` | integer | Rank inside representation by mean delta. |
| `rank_decoy_penalized_delta` | integer | Rank inside representation by min delta. |

## 5. `bms_fu02c_representation_motif_enrichment.csv`

| field name | type | description |
|---|---:|---|
| `representation_id` | string | Representation id. |
| `score_name` | string | Score used for top-k. |
| `topk_label` | string | Top-k label. |
| `k` | integer | Top-k size. |
| `hh_count` | integer | H,H count. |
| `hp_count` | integer | H,P count. |
| `hh_fraction` | float | H,H fraction. |
| `hp_fraction` | float | H,P fraction. |
| `hh_enrichment_ratio` | float | H,H enrichment relative to 1/3 baseline. |
| `hp_enrichment_ratio` | float | H,P enrichment relative to 2/3 baseline. |
| `top_edges` | string | Top edge ids. |

## 6. `bms_fu02c_consensus_carriers.csv`

| field name | type | description |
|---|---:|---|
| `edge_key` | string | Canonical edge id. |
| `representations_present` | string | Representations present. |
| `positive_representations` | string | Representations with positive mean delta. |
| `decoy_positive_representations` | string | Representations with positive min delta. |
| `top10_representations` | string | Representations where edge is top 10. |
| `top20_representations` | string | Representations where edge is top 20. |
| `top30_representations` | string | Representations where edge is top 30. |
| `top30_representation_count` | integer | Number of top-30 representation hits. |
| `mean_delta_across_representations` | float | Mean delta across representations. |
| `min_decoy_delta_across_representations` | float | Minimum min-delta across representations. |
| `consensus_label` | string | Consensus label. |

Consensus labels:

```text
hh_consensus_all_representations
hh_consensus_two_representations
hp_secondary_carrier
representation_specific_candidate
decoy_reproduced_or_unstable
```

## 7. Scope note

FU02c-v0 skips `graph_distance_shells` contexts by default.

Allowed wording:

```text
FU02c-v0 tests representation-resolved carrier dominance for deterministic
non-shell envelope reconstructions.
```
