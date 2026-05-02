# BMS-FU02b — Runner Field List

Date: 2026-05-02  
Project: Gravitation und RaumZeit / Quantum-Spacetime-Bridge  
Recommended repo target: `docs/BMS_FU02B_RUNNER_FIELD_LIST.md`  
Status: Companion field list for BMS-FU02b carrier sharpness and rank-stability extension

---

## 1. Purpose

BMS-FU02b sharpens the broad FU02-v0 carrier-positive ranking by adding top-k sets, motif enrichment, decoy-penalized scoring and rank-stability diagnostics.

Working question:

```text
Welche Träger bleiben oben, wenn Rankingdruck und Decoy-Strafe dazukommen?
```

---

## 2. Config fields

| field name | type | description |
|---|---:|---|
| `run.run_id` | string | Stable run identifier. |
| `run.output_dir` | string | Output directory for FU02b artifacts. |
| `run.random_seed` | integer | Seed placeholder; FU02b-v0 is deterministic. |
| `inputs.fu02_output_dir` | string | FU02 output directory. |
| `inputs.c60_edges_csv` | string | Validated C60 edge table. |
| `inputs.c60_nodes_csv` | string | Validated C60 node table. |
| `inputs.c60_faces_csv` | string | Validated C60 face table. |
| `inputs.c60_graph_manifest_json` | string | C60 validation manifest. |
| `sharpness.topk_values` | list[integer] | Top-k sets to compute. |
| `sharpness.percentile_top_fractions` | list[float] | Reserved percentile top fractions. |
| `sharpness.decoy_penalty_mode` | string | Null penalty rule; v0 uses `max_null`. |
| `sharpness.topology_sensitive_representations` | list[string] | Topology-sensitive representations. |
| `sharpness.composite_weights.*` | float | Weights for composite sharpness score. |
| `labeling.sharp_top_rank_cutoff` | integer | Rank cutoff for sharp carrier labels. |
| `labeling.survivor_top_rank_cutoff` | integer | Rank cutoff for decoy survivor label. |
| `labeling.min_positive_topology_representation_count` | integer | Minimum topology persistence count. |
| `labeling.min_decoy_penalized_score` | float | Minimum decoy-penalized score. |

---

## 3. Edge sharpness scores

Output:

```text
bms_fu02b_edge_sharpness_scores.csv
```

| field name | type | description |
|---|---:|---|
| `edge_key` | string | Canonical C60 edge id. |
| `source` | string | Source node id. |
| `target` | string | Target node id. |
| `edge_type` | string | C60 edge type: `6_6` or `5_6`. |
| `shared_face_types` | string | Face signature: `H,H` or `H,P`. |
| `score_fu02_mean_null` | float | FU02-v0 score: real retention minus mean null retention. |
| `score_decoy_penalized` | float | Real retention minus maximum null retention. |
| `score_topology_sensitive` | float | FU02b-v0 topology persistence proxy score. |
| `score_core_variant_stability` | float | Fraction of FU01c core variants with positive retention. |
| `real_retention_rate` | float | Real retention rate from FU02. |
| `mean_null_retention_rate` | float | Mean null retention rate from FU02. |
| `max_null_retention_rate` | float | Maximum null retention rate parsed from FU02 null rates. |
| `rank_fu02_mean_null` | integer | Descending rank by FU02-v0 score. |
| `rank_decoy_penalized` | integer | Descending rank by decoy-penalized score. |
| `rank_topology_sensitive` | integer | Descending rank by topology-sensitive proxy score. |
| `rank_core_variant_stability` | integer | Descending rank by core-variant stability score. |
| `sharpness_score` | float | Weighted composite rank-normalized sharpness score. |
| `sharpness_rank` | integer | Descending rank by sharpness score. |
| `sharpness_vote_count` | integer | Number of score definitions where the edge enters the strict top-k set. |
| `topk_memberships` | string | Semicolon-separated top-k memberships. |
| `rank_std` | float | Standard deviation across rank definitions. |
| `best_rank` | integer | Best rank across score definitions. |
| `worst_rank` | integer | Worst rank across score definitions. |
| `top10_count` | integer | Number of rank definitions where edge is top 10. |
| `top20_count` | integer | Number of rank definitions where edge is top 20. |
| `top30_count` | integer | Number of rank definitions where edge is top 30. |
| `positive_representation_count` | integer | FU02 positive representation count. |
| `positive_representations` | string | FU02 positive representation labels. |
| `positive_topology_representation_count` | integer | FU02 topology-sensitive positive representation count. |
| `positive_topology_representations` | string | FU02 topology-sensitive positive representation labels. |
| `positive_core_variant_count` | integer | FU02 positive core variant count. |
| `positive_core_variants` | string | FU02 positive core variants. |
| `fu02_candidate_label` | string | FU02-v0 broad candidate label. |
| `candidate_label` | string | FU02b sharp candidate label. |
| `null_retention_rates_json` | JSON string | FU02 null retention rates. |

---

## 4. Candidate labels

| label | meaning |
|---|---|
| `sharp_hh_seam_carrier` | Top sharpness carrier with H,H / 6:6 seam character. |
| `sharp_hp_boundary_carrier` | Top sharpness carrier with H,P / 5:6 pentagon-boundary character. |
| `sharp_cross_representation_carrier` | Top sharpness carrier not captured by the motif-specific labels. |
| `sharp_topology_carrier` | High topology-sensitive rank with topology persistence. |
| `decoy_penalized_survivor` | Survives max-null penalty and ranks high in decoy-penalized score. |
| `decoy_reproduced_candidate` | Positive FU02 score but decoy-penalized score is non-positive. |
| `motif_enriched_candidate` | High sharpness rank but not meeting stricter labels. |
| `broad_positive_only` | Broad FU02-positive but not sharp under FU02b. |
| `inconclusive_or_tie_sensitive` | Weak or construction-sensitive. |

---

## 5. Motif enrichment

Output:

```text
bms_fu02b_motif_enrichment.csv
```

| field name | type | description |
|---|---:|---|
| `score_name` | string | Score used to define the top-k set. |
| `topk_label` | string | Top-k label, e.g. `top_10`. |
| `k` | integer | Requested number of edges. |
| `hh_count` | integer | H,H edge count in the selected set. |
| `hp_count` | integer | H,P edge count in the selected set. |
| `hh_fraction` | float | Fraction of H,H edges. |
| `hp_fraction` | float | Fraction of H,P edges. |
| `hh_enrichment_ratio` | float | H,H enrichment relative to full C60 baseline 1/3. |
| `hp_enrichment_ratio` | float | H,P enrichment relative to full C60 baseline 2/3. |
| `top_edges` | string | Top edge ids in that set. |

---

## 6. Rank stability matrix

Output:

```text
bms_fu02b_rank_stability_matrix.csv
```

| field name | type | description |
|---|---:|---|
| `edge_key` | string | Canonical edge id. |
| `rank_fu02_mean_null` | integer | Rank by FU02 mean-null score. |
| `rank_decoy_penalized` | integer | Rank by decoy-penalized score. |
| `rank_topology_sensitive` | integer | Rank by topology-sensitive score. |
| `rank_core_variant_stability` | integer | Rank by core-variant stability. |
| `sharpness_rank` | integer | Rank by composite sharpness. |
| `rank_std` | float | Rank standard deviation. |
| `best_rank` | integer | Best rank across score definitions. |
| `worst_rank` | integer | Worst rank across score definitions. |
| `top10_count` | integer | Number of score definitions where edge is top 10. |
| `top20_count` | integer | Number of score definitions where edge is top 20. |
| `top30_count` | integer | Number of score definitions where edge is top 30. |

---

## 7. Decoy penalty profiles

Output:

```text
bms_fu02b_decoy_penalty_profiles.csv
```

| field name | type | description |
|---|---:|---|
| `edge_key` | string | Canonical edge id. |
| `real_retention_rate` | float | Real retention rate. |
| `mean_null_retention_rate` | float | Mean null retention rate. |
| `max_null_retention_rate` | float | Maximum null retention rate. |
| `score_fu02_mean_null` | float | FU02 mean-null score. |
| `score_decoy_penalized` | float | Decoy-penalized score. |
| `degree_preserving_rewire_retention` | float | Retention in degree-preserving null. |
| `edge_class_shuffle_retention` | float | Retention in edge-class shuffle null. |
| `motif_class_preserving_edge_swap_proxy_retention` | float | Retention in motif-proxy null. |
| `core_seeded_decoy_retention` | float | Retention in core-seeded decoy null. |

---

## 8. Node sharpness scores

Output:

```text
bms_fu02b_node_sharpness_scores.csv
```

| field name | type | description |
|---|---:|---|
| `node_id` | string | C60 node id. |
| `degree` | integer | Node degree. |
| `incident_6_6_count` | integer | Number of incident 6:6 edges. |
| `incident_5_6_count` | integer | Number of incident 5:6 edges. |
| `fu02_node_load_bearing_score` | float | FU02 node score. |
| `incident_edge_count` | integer | Number of incident scored edges. |
| `mean_incident_sharpness_score` | float | Mean sharpness score of incident edges. |
| `max_incident_sharpness_score` | float | Maximum incident sharpness score. |
| `mean_incident_decoy_penalized_score` | float | Mean incident decoy-penalized edge score. |
| `sharp_incident_edge_count_top20` | integer | Incident edges in top 20 sharpness rank. |
| `sharp_incident_edge_count_top30` | integer | Incident edges in top 30 sharpness rank. |
| `incident_candidate_label_counts` | JSON string | FU02b labels among incident edges. |
| `top_incident_edges` | string | Incident edges sorted by sharpness. |
| `node_sharpness_rank` | integer | Node rank by mean incident sharpness. |

---

## 9. Scope note

FU02b-v0 uses FU02 persistence fields to compute topology-sensitive score. It does not fully recompute representation-specific edge deltas from FU01c contexts.

Allowed wording:

```text
FU02b-v0 provides sharpness ranking from FU02 aggregate outputs.
```

Not allowed:

```text
FU02b-v0 fully resolves representation-specific carrier deltas.
```
