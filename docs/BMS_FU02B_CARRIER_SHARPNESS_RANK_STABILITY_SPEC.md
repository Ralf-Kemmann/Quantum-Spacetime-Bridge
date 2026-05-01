# BMS-FU02b — Carrier Sharpness and Rank-Stability Extension Specification

Date: 2026-05-02  
Project: Gravitation und RaumZeit / Quantum-Spacetime-Bridge  
Recommended repo target: `docs/BMS_FU02B_CARRIER_SHARPNESS_RANK_STABILITY_SPEC.md`  
Status: Specification only; no numerical run completed yet

---

## 1. Purpose

BMS-FU02b follows BMS-FU02-v0.

FU02-v0 established:

```text
The full C60 bond graph participates in the broad load-bearing score.

All 90 C60 bond edges received a positive carrier label under the permissive
v0 rule.

However, the ranking was highly structured:
  H,H / 6:6 seam edges had the strongest average score.
  H,P / 5:6 pentagon-boundary edges were positive but weaker.
```

FU02b asks the sharper question:

```text
Welche Träger sind wirklich scharf,
rangstabil und nicht nur breit positiv?
```

Scientific formulation:

```text
Which C60 carrier candidates remain top-ranked under stricter scoring,
top-k selection, decoy penalization, representation separation, and motif
enrichment analysis?
```

Internal image:

```text
FU02-v0:
  Der ganze Ball beteiligt sich,
  aber H-H-Nähte tragen am stärksten.

FU02b:
  Jetzt trennen wir tragende Lastfäden von bloßer Mitbeteiligung.
```

---

## 2. Motivation

FU02-v0 is useful but too broad as a classifier.

Its candidate labels were:

```text
cross_representation_structure_carrier: 76
topology_only_structure_carrier: 14
```

Thus:

```text
candidate_carrier_count = 90
```

This means:

```text
The v0 label rule is not sharp enough.
```

FU02b should turn FU02-v0 from:

```text
broad carrier-positive ranking
```

into:

```text
sharp carrier discrimination.
```

---

## 3. Working questions

Main question:

```text
Which C60 edges and motifs remain strongest after ranking, top-k selection,
topology-only separation and decoy penalization?
```

Sub-questions:

```text
1. Which edges remain in the top 10, top 20 and top 30 by multiple scores?

2. Are H,H / 6:6 seam edges enriched in the top-k carrier sets?

3. Are H,P / 5:6 pentagon-boundary edges systematically weaker, or do some
   H,P edges become sharp carriers?

4. Which edges remain strong in topology-only and graph-distance representations
   separately from bond_class_weighted?

5. Which edges lose rank after core_seeded_decoy or edge_class_shuffle penalties?

6. Which carrier ranks are stable across core variants?

7. Which node neighborhoods concentrate the sharpest carrier edges?

8. Can FU02b define a smaller, defensible sharp-carrier set?
```

---

## 4. Recommended block label

```text
BMS-FU02b
```

Recommended output directory:

```text
runs/BMS-FU02b/carrier_sharpness_rank_stability_open/
```

Recommended repo files:

```text
docs/BMS_FU02B_CARRIER_SHARPNESS_RANK_STABILITY_SPEC.md
docs/BMS_FU02B_RUNNER_FIELD_LIST.md
docs/BMS_FU02B_CARRIER_SHARPNESS_RESULT_NOTE.md

data/bms_fu02b_carrier_sharpness_config.yaml
scripts/run_bms_fu02b_carrier_sharpness_rank_stability.py
```

---

## 5. Input artifacts

Primary FU02 outputs:

```text
runs/BMS-FU02/load_bearing_pattern_analysis_open/bms_fu02_edge_load_bearing_scores.csv
runs/BMS-FU02/load_bearing_pattern_analysis_open/bms_fu02_node_load_bearing_scores.csv
runs/BMS-FU02/load_bearing_pattern_analysis_open/bms_fu02_null_resistance_profiles.csv
runs/BMS-FU02/load_bearing_pattern_analysis_open/bms_fu02_motif_load_bearing_summary.csv
runs/BMS-FU02/load_bearing_pattern_analysis_open/bms_fu02_candidate_structure_carriers.csv
runs/BMS-FU02/load_bearing_pattern_analysis_open/bms_fu02_run_manifest.json
runs/BMS-FU02/load_bearing_pattern_analysis_open/bms_fu02_warnings.json
```

Primary FU01c outputs needed for representation-specific recomputation:

```text
runs/BMS-FU01c/c60_motif_topology_extension_open/bms_fu01c_edges.csv
runs/BMS-FU01c/c60_motif_topology_extension_open/bms_fu01c_real_vs_null_summary.csv
runs/BMS-FU01c/c60_motif_topology_extension_open/bms_fu01c_run_manifest.json
runs/BMS-FU01c/c60_motif_topology_extension_open/bms_fu01c_warnings.json
```

C60 audit inputs:

```text
data/bms_fu01_c60_nodes.csv
data/bms_fu01_c60_edges.csv
data/bms_fu01_c60_faces.csv
data/bms_fu01_c60_graph_manifest.json
```

---

## 6. Core FU02b concepts

### 6.1 Rank stability

For each edge:

```text
rank_stability(e) =
  number of score definitions / representation views / top-k sets
  in which e remains highly ranked.
```

Recommended top-k sets:

```text
top_10
top_20
top_30
```

Recommended percentile bands:

```text
top_10_percent
top_20_percent
top_33_percent
```

Since C60 has 90 bond edges:

```text
top_10_percent ≈ top 9
top_20_percent = top 18
top_33_percent ≈ top 30
```

---

### 6.2 Topology-only sharpness

FU02b should separate:

```text
bond_class_weighted_score
topology_only_equal_weight_score
graph_distance_similarity_d3_score
```

Then define:

```text
topology_sensitive_score(e) =
  mean(
    topology_only_equal_weight_delta(e),
    graph_distance_similarity_d3_delta(e)
  )
```

Interpretation:

```text
An edge is topology-sensitive if it remains strong without explicit 6:6 / 5:6
weights and in graph-distance representation.
```

---

### 6.3 Decoy-penalized score

Recommended conservative score:

```text
L_decoy_penalized(e) =
  P_real_retained(e) - max_N P_null_retained(e)
```

where max_N is taken over:

```text
degree_preserving_rewire
edge_class_shuffle
motif_class_preserving_edge_swap_proxy
core_seeded_decoy
```

Interpretation:

```text
An edge receives high decoy-penalized score only if it beats the strongest
tested null reproduction channel.
```

Less strict auxiliary score:

```text
L_mean_penalized(e) =
  P_real_retained(e) - mean_N P_null_retained(e)
```

FU02-v0 effectively used the less strict mean-null form.

FU02b should report both.

---

### 6.4 Shuffle penalty and decoy penalty

Separate penalties:

```text
edge_class_shuffle_penalty(e) =
  P_edge_class_shuffle_retained(e)

core_seeded_decoy_penalty(e) =
  P_core_seeded_decoy_retained(e)

motif_proxy_penalty(e) =
  P_motif_class_preserving_edge_swap_proxy_retained(e)
```

Interpretation:

```text
If an edge remains high only under mean-null scoring but is highly reproduced
by core-seeded decoy, it should be downgraded.
```

---

### 6.5 Motif enrichment

For each top-k set, compute motif composition:

```text
H,H count
H,P count
H,H fraction
H,P fraction
```

Compare against full graph baseline:

```text
C60 full graph:
  H,H = 30 / 90 = 1/3
  H,P = 60 / 90 = 2/3
```

Enrichment ratio:

```text
enrichment_HH(top_k) =
  fraction_HH(top_k) / (30/90)
```

```text
enrichment_HP(top_k) =
  fraction_HP(top_k) / (60/90)
```

Interpretation:

```text
If top_10 contains 9 H,H edges, then:
  fraction_HH = 0.9
  enrichment_HH = 0.9 / 0.333... ≈ 2.7
```

This is a simple, transparent motif enrichment readout.

---

## 7. Recommended score definitions

FU02b should compute the following edge scores.

### 7.1 Existing FU02 score

```text
score_fu02_mean_null =
  real_retention_rate - mean_null_retention_rate
```

### 7.2 Decoy-penalized score

```text
score_decoy_penalized =
  real_retention_rate - max_null_retention_rate
```

where max_null_retention_rate is the maximum over all null-family retention rates.

### 7.3 Topology-sensitive score

```text
score_topology_sensitive =
  mean positive delta over:
    topology_only_equal_weight
    graph_distance_similarity_d3
```

This requires representation-specific recomputation from FU01c or use of a representation-aware intermediate table.

### 7.4 Core-variant stability score

```text
score_core_variant_stability =
  number of core variants in which edge has positive delta / 4
```

Core variants:

```text
local_6_6_patch_core
distributed_6_6_core
local_5_6_pentagon_boundary_core
distributed_5_6_pentagon_boundary_core
```

### 7.5 Composite sharpness score

Recommended first-pass composite:

```text
sharpness_score =
  0.35 * rank_norm(score_decoy_penalized)
+ 0.30 * rank_norm(score_topology_sensitive)
+ 0.20 * rank_norm(score_core_variant_stability)
+ 0.15 * rank_norm(score_fu02_mean_null)
```

Alternative transparent non-weighted score:

```text
sharpness_vote_count =
  I(edge in top_10 score_decoy_penalized)
+ I(edge in top_10 score_topology_sensitive)
+ I(edge in top_10 score_core_variant_stability)
+ I(edge in top_10 score_fu02_mean_null)
```

FU02b-v0 should prefer both:

```text
1. sharpness_score
2. sharpness_vote_count
```

because the vote count is easier to audit.

---

## 8. Candidate labels

FU02b should replace broad FU02-v0 labels with sharper labels:

```text
sharp_cross_representation_carrier
sharp_topology_carrier
sharp_hh_seam_carrier
sharp_hp_boundary_carrier
decoy_penalized_survivor
decoy_reproduced_candidate
motif_enriched_candidate
broad_positive_only
inconclusive_or_tie_sensitive
```

Suggested decision rules:

### 8.1 sharp_cross_representation_carrier

```text
sharpness_score in top 20
AND positive in at least two representations
AND decoy_penalized_score > 0
```

### 8.2 sharp_topology_carrier

```text
score_topology_sensitive in top 20
AND positive in topology_only_equal_weight
AND positive in graph_distance_similarity_d3
```

### 8.3 sharp_hh_seam_carrier

```text
edge_type = 6_6
AND shared_face_types = H,H
AND edge in top 20 sharpness_score
```

### 8.4 sharp_hp_boundary_carrier

```text
edge_type = 5_6
AND shared_face_types = H,P
AND edge in top 20 sharpness_score
```

### 8.5 decoy_penalized_survivor

```text
score_decoy_penalized > 0
AND edge in top 30 score_decoy_penalized
```

### 8.6 decoy_reproduced_candidate

```text
core_seeded_decoy_retention_rate is high
OR score_decoy_penalized <= 0
while FU02 mean-null score is positive
```

### 8.7 broad_positive_only

```text
FU02 mean-null score positive
but not in top 30 of any sharp score
```

---

## 9. Recommended outputs

Output directory:

```text
runs/BMS-FU02b/carrier_sharpness_rank_stability_open/
```

Expected files:

```text
bms_fu02b_edge_sharpness_scores.csv
bms_fu02b_node_sharpness_scores.csv
bms_fu02b_topk_edge_sets.csv
bms_fu02b_motif_enrichment.csv
bms_fu02b_rank_stability_matrix.csv
bms_fu02b_decoy_penalty_profiles.csv
bms_fu02b_sharp_candidate_carriers.csv
bms_fu02b_sharp_candidate_neighborhoods.csv
bms_fu02b_run_manifest.json
bms_fu02b_warnings.json
bms_fu02b_config_resolved.yaml
```

Optional later:

```text
bms_fu02b_top_carrier_network_map.png
bms_fu02b_hh_vs_hp_score_distribution.png
```

---

## 10. Output field list — edge sharpness scores

| field name | type | description |
|---|---:|---|
| `edge_key` | string | Canonical edge id. |
| `source` | string | Source node id. |
| `target` | string | Target node id. |
| `edge_type` | string | `6_6` or `5_6`. |
| `shared_face_types` | string | `H,H` or `H,P`. |
| `score_fu02_mean_null` | float | FU02-v0 mean-null load-bearing score. |
| `score_decoy_penalized` | float | Real retention minus max null retention. |
| `score_topology_sensitive` | float | Topology-only / graph-distance score. |
| `score_core_variant_stability` | float | Fraction of core variants with positive retention. |
| `rank_fu02_mean_null` | integer | Rank by FU02 score. |
| `rank_decoy_penalized` | integer | Rank by decoy-penalized score. |
| `rank_topology_sensitive` | integer | Rank by topology-sensitive score. |
| `rank_core_variant_stability` | integer | Rank by core-variant stability. |
| `sharpness_score` | float | Composite rank-normalized sharpness score. |
| `sharpness_rank` | integer | Rank by composite sharpness score. |
| `sharpness_vote_count` | integer | Number of top-k sharpness criteria met. |
| `topk_memberships` | string | Semicolon-separated top-k membership labels. |
| `candidate_label` | string | FU02b sharp candidate label. |
| `null_retention_rates_json` | JSON string | Null retention rates inherited/recomputed. |

---

## 11. Output field list — motif enrichment

| field name | type | description |
|---|---:|---|
| `score_name` | string | Score used for top-k set. |
| `topk_label` | string | Top-k set label. |
| `k` | integer | Number of selected edges. |
| `hh_count` | integer | Number of H,H / 6:6 edges. |
| `hp_count` | integer | Number of H,P / 5:6 edges. |
| `hh_fraction` | float | H,H fraction in top-k set. |
| `hp_fraction` | float | H,P fraction in top-k set. |
| `hh_enrichment_ratio` | float | H,H fraction divided by full-graph baseline 1/3. |
| `hp_enrichment_ratio` | float | H,P fraction divided by full-graph baseline 2/3. |
| `top_edges` | string | Top edge ids in that set. |

---

## 12. Output field list — rank stability matrix

| field name | type | description |
|---|---:|---|
| `edge_key` | string | Canonical edge id. |
| `rank_fu02_mean_null` | integer | Rank by FU02-v0 score. |
| `rank_decoy_penalized` | integer | Rank by decoy-penalized score. |
| `rank_topology_sensitive` | integer | Rank by topology-sensitive score. |
| `rank_core_variant_stability` | integer | Rank by core stability score. |
| `rank_std` | float | Standard deviation of available ranks. |
| `best_rank` | integer | Best rank across score definitions. |
| `worst_rank` | integer | Worst rank across score definitions. |
| `top10_count` | integer | Number of score definitions where edge is in top 10. |
| `top20_count` | integer | Number of score definitions where edge is in top 20. |
| `top30_count` | integer | Number of score definitions where edge is in top 30. |

---

## 13. Interpretation patterns

### Pattern A — H,H enriched in top-k

Allowed:

```text
FU02b sharp-carrier ranks are enriched for H,H / 6:6 seam edges relative to the
full C60 edge baseline.
```

### Pattern B — H,P survives decoy penalty

Allowed:

```text
Some pentagon-boundary H,P / 5:6 edges survive sharpness filtering, indicating
that the carrier set is not exclusively H,H.
```

### Pattern C — topology-sensitive and decoy-penalized scores agree

Allowed:

```text
The sharpest carrier candidates are not merely weighted-edge artifacts; they
remain visible in topology-sensitive views and survive decoy penalization.
```

### Pattern D — decoy penalty collapses many edges

Allowed:

```text
The broad FU02-v0 carrier-positive set is partly explained by decoy-reproducible
retention; FU02b therefore narrows the defensible carrier set.
```

### Pattern E — ranks unstable

Allowed:

```text
Carrier ranking is construction- or score-dependent; FU02b should be read as
diagnostic ranking rather than sharp structure extraction.
```

---

## 14. Claim boundary

Allowed:

```text
BMS-FU02b sharpens the FU02-v0 carrier ranking by adding top-k analysis,
motif enrichment, representation-sensitive scores and decoy-penalized scores.
```

Allowed after positive result:

```text
BMS-FU02b identifies a smaller set of sharp C60 carrier candidates that remain
high-ranked under topology-sensitive and decoy-penalized scoring.
```

Not allowed:

```text
The sharp carriers are physical spacetime atoms.
C60 proves emergent spacetime.
Global C60 symmetry has been fully recovered.
A physical metric has been recovered.
The bridge recognizes molecules.
```

---

## 15. Bridge relevance

FU02b sharpens the Bridge-relevant statement.

FU02-v0 suggested:

```text
relations have roles.
```

FU02b asks:

```text
which roles are sharp, stable and not cheaply reproduced?
```

Bridge-facing cautious statement:

```text
BMS-FU02b tests whether the load-bearing relational patterns identified in C60
remain sharp under stricter ranking, topology-sensitive scoring and decoy
penalization. A positive result would support the view that only a subset of
relations act as robust carriers of geometry-readable structure.
```

Internal formulation:

```text
Nicht jeder Faden trägt gleich.
FU02b sucht die Lastfäden.
```

---

## 16. Recommended immediate implementation scope

FU02b-v0 should implement:

```text
1. Load FU02 edge score table.
2. Parse null_retention_rates_json.
3. Compute max-null decoy-penalized score.
4. Compute simple topology-sensitive score from available FU02 representation
   persistence fields where possible.
5. Compute ranks and top-k sets.
6. Compute H,H / H,P motif enrichment for top-k sets.
7. Produce sharp candidate labels.
8. Write result tables and manifest.
```

If representation-specific recomputation from FU01c is too heavy for v0, explicitly mark:

```text
topology_sensitive_score in FU02b-v0 is based on FU02 persistence fields,
not full context-level recomputation.
```

Then a later FU02c can add full representation-resolved recomputation.

---

## 17. Minimal commit plan

Commit this specification first:

```bash
cd ~/Downloads/deBroglie_Kaster_Theorie/quantum-spacetime-bridge

cp ~/Downloads/BMS_FU02B_CARRIER_SHARPNESS_RANK_STABILITY_SPEC.md \
  docs/BMS_FU02B_CARRIER_SHARPNESS_RANK_STABILITY_SPEC.md

git add docs/BMS_FU02B_CARRIER_SHARPNESS_RANK_STABILITY_SPEC.md

git status --short

git commit -m "Add BMS-FU02b carrier sharpness rank stability specification"

git push
```

Implementation should follow after the scoring rules are accepted.

---

## 18. Internal summary

```text
FU02-v0:
  Der ganze Ball beteiligt sich,
  aber H-H / 6:6-Nähte tragen am stärksten.

FU02b:
  Jetzt prüfen wir:
    Welche davon bleiben Top-Träger?
    Welche überleben Decoy-Strafe?
    Welche sind topology-only stabil?
    Welche sind nur breit positiv?
```
