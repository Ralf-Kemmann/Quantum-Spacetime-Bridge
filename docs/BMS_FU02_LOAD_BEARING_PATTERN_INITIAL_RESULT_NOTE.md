# BMS-FU02 — Load-Bearing Pattern Analysis Initial Result Note

Date: 2026-05-01  
Project: Gravitation und RaumZeit / Quantum-Spacetime-Bridge  
Recommended repo target: `docs/BMS_FU02_LOAD_BEARING_PATTERN_INITIAL_RESULT_NOTE.md`  
Status: Initial result note for BMS-FU02-v0

---

## 1. Purpose

BMS-FU02 follows the FU01/FU01b/FU01c C60 calibration chain.

FU01/FU01b/FU01c established:

```text
FU01:
  A local 6:6 seam is retained against degree-preserving rewires.

FU01b:
  Alternative local and distributed 6:6 / 5:6 core selections also carry signal.

FU01c:
  The signal does not collapse when explicit 6:6 / 5:6 edge weights are removed.
  Topology-only and graph-distance representations remain informative.
```

FU02 asks the next question:

```text
Welche Muster tragen — und warum tragen sie?
```

Scientific formulation:

```text
Which C60 edges, nodes and local motif classes are repeatedly retained across
FU01c representations and null contrasts, and what structural features
characterize them?
```

Internal formulation:

```text
Nicht mehr nur:
  Der Ball trägt.

Sondern:
  Welche Fäden tragen besonders?
```

---

## 2. Run context

Runner:

```text
scripts/run_bms_fu02_load_bearing_pattern_analysis.py
```

Config:

```text
data/bms_fu02_load_bearing_pattern_config.yaml
```

Output directory:

```text
runs/BMS-FU02/load_bearing_pattern_analysis_open/
```

Run id:

```text
BMS-FU02_load_bearing_pattern_analysis_open
```

Input FU01c run:

```text
BMS-FU01c_c60_motif_topology_extension_open
```

Input C60 graph:

```text
c60_valid: true
node_count: 60
bond_edge_count: 90
face_count: 32
```

---

## 3. Warnings and scope boundary

The run reports one informational warning:

```text
FU02-v0 skipped 144 graph_distance_shells contexts to avoid hidden
reconstruction assumptions.
```

Interpretation:

```text
This is acceptable and desirable for FU02-v0.
```

Reason:

```text
The graph_distance_shells construction cannot be reconstructed edge-by-edge
from the available FU01c summary without adding hidden assumptions. FU02-v0
therefore leaves those contexts out of edge/node load-bearing reconstruction.
```

This follows the project transparency rule:

```text
lieber eine Lücke offen markieren
als heimlich etwas rekonstruieren.
```

---

## 4. Row counts and labels

Run manifest:

```text
edge_score_count: 90
node_score_count: 60
candidate_carrier_count: 90

candidate_label_counts:
  cross_representation_structure_carrier: 76
  topology_only_structure_carrier: 14

motif_counts:
  H,H: 30
  H,P: 60
```

Important methodological warning:

```text
All 90 C60 bond edges receive a positive carrier label in FU02-v0.
```

This must not be overread as:

```text
Every edge is equally important.
```

Instead, it means:

```text
The FU02-v0 candidate-label rule is too permissive for final discrimination.
The informative layer is currently the ranking, score distribution, motif
contrast and top-carrier concentration.
```

Internal image:

```text
Der ganze Ball trägt irgendwie.
Aber manche Nähte tragen deutlich mehr Last.
```

---

## 5. Main result

The strongest edge carriers are dominated by 6:6 H-H seams.

Top-ranked edge examples:

```text
c60_050--c60_059  6_6  H,H
  load_bearing_score = 0.45643518518518533
  real_retention_rate = 0.8703703703703703
  mean_null_retention_rate = 0.413935185185185

c60_044--c60_048  6_6  H,H
  load_bearing_score = 0.4491898148148148
  real_retention_rate = 0.8333333333333334
  mean_null_retention_rate = 0.3841435185185186

c60_045--c60_058  6_6  H,H
  load_bearing_score = 0.44858796296296305
  real_retention_rate = 0.8333333333333334
  mean_null_retention_rate = 0.3847453703703703

c60_055--c60_060  6_6  H,H
  load_bearing_score = 0.4461111111111112
  real_retention_rate = 0.8703703703703703
  mean_null_retention_rate = 0.42425925925925917
```

Interpretation:

```text
The strongest load-bearing edge candidates are not random across the C60 graph;
they concentrate in H-H / 6:6 seam structure.
```

---

## 6. Motif-level result

Motif summary:

```text
H,H:
  edge_count = 30
  mean_load_bearing_score = 0.393266975308642
  max_load_bearing_score = 0.45643518518518533
  labels:
    cross_representation_structure_carrier: 27
    topology_only_structure_carrier: 3

H,P:
  edge_count = 60
  mean_load_bearing_score = 0.26234259259259257
  max_load_bearing_score = 0.36812500000000004
  labels:
    cross_representation_structure_carrier: 49
    topology_only_structure_carrier: 11
```

Key quantitative contrast:

```text
mean_score(H,H) - mean_score(H,P)
  = 0.393266975308642 - 0.26234259259259257
  ≈ 0.13092438271604945
```

Ratio:

```text
mean_score(H,H) / mean_score(H,P)
  ≈ 1.50
```

Interpretation:

```text
6:6 / H-H seams carry a substantially stronger average load-bearing score than
5:6 / H-P pentagon-boundary edges in FU02-v0.
```

This supports a more specific statement than FU01c alone:

```text
The C60 load-bearing pattern is not merely topology-positive everywhere; it is
ranked, with hexagon-hexagon seam edges forming the strongest carrier class.
```

Internal image:

```text
Alle Fäden gehören zum Ball.
Aber die H-H-Nähte tragen im Mittel mehr Zug.
```

---

## 7. Node-level result

Top node candidates are concentrated in the high-scoring carrier region:

```text
c60_054
  load_bearing_score = 0.38635030864197545
  real_retention_rate = 0.8024691358024691
  mean_null_retention_rate = 0.4161188271604937
  positive topology reps = graph_distance_similarity_d3;topology_only_equal_weight
  retained_edge_incidence_count = 3

c60_059
  load_bearing_score = 0.38547067901234583
  real_retention_rate = 0.8148148148148148
  mean_null_retention_rate = 0.42934413580246894
  retained_edge_incidence_count = 3

c60_060
  load_bearing_score = 0.38314043209876547
  real_retention_rate = 0.8148148148148148
  mean_null_retention_rate = 0.4316743827160493
  retained_edge_incidence_count = 3

c60_055
  load_bearing_score = 0.38108796296296304
  real_retention_rate = 0.8024691358024691
  mean_null_retention_rate = 0.4213811728395061
  retained_edge_incidence_count = 3
```

Interpretation:

```text
The strongest node candidates are not isolated single-edge artifacts. They sit
on multiple retained carrier edges and form local load-bearing neighborhoods.
```

Internal image:

```text
Nicht nur einzelne Fäden.
Da sitzen kleine Knotenpunkte im Gewebe.
```

---

## 8. What FU02-v0 tells us about “why”

FU02-v0 gives a first explanation layer.

The strongest carriers share:

```text
1. H-H / 6:6 seam character.
2. High real retention rate.
3. Lower null retention rate.
4. Visibility in topology_only_equal_weight.
5. Visibility in graph_distance_similarity_d3.
6. Recurrence across all four FU01b/FU01c core variants.
7. Local node clustering through shared high-score endpoints.
```

This means the strongest patterns are not just:

```text
large edge weights
```

because they also remain positive in topology-only and graph-distance contexts.

They are also not just:

```text
one selected core artifact
```

because the top edges are positive across all four core variants.

Defensive interpretation:

```text
The strongest FU02-v0 carriers are local seam-like relational structure
carriers. Their stability appears to be associated with 6:6 H-H motif class,
multi-core recurrence and topology-sensitive retention.
```

---

## 9. What FU02-v0 does NOT prove

FU02-v0 does not prove:

```text
global C60 symmetry recovery
physical spacetime geometry
quantum chemistry
a physical metric
that every C60 edge is equally load-bearing
that the top carriers are unique physical objects
```

FU02-v0 also has an important methodological limitation:

```text
The candidate-label rule is too broad because it labels all 90 bond edges as
carriers.
```

Therefore:

```text
FU02-v0 is a ranking and motif-contrast result, not yet a sharp classifier.
```

---

## 10. Interpretation for the Bridge

FU02-v0 advances the Bridge argument in a cautious but useful way.

Bridge-facing statement:

```text
BMS-FU02-v0 suggests that relational structure in the controlled C60 object is
not uniformly informative. Although all bond edges show positive candidate
status under the permissive v0 rule, the strongest load-bearing scores
concentrate in H-H / 6:6 seam motifs and in local node neighborhoods that remain
visible under topology-only and graph-distance representations. This supports
the idea that relational information has role structure, not only value
structure.
```

Short internal statement:

```text
Die Beziehungssuppe hat nicht nur Werte.
Sie hat Rollen.
```

This is important because the Bridge should not claim:

```text
every relation becomes geometry
```

but rather:

```text
some relations may function as geometry-readable structure carriers.
```

---

## 11. Why the top H-H seam result matters

H-H / 6:6 seams are special in the C60 graph because they connect two hexagon faces.

FU02-v0 shows that these seams have:

```text
higher mean load-bearing score
higher top scores
strong cross-representation visibility
```

compared with H-P / 5:6 pentagon-boundary edges.

This suggests:

```text
The strongest C60 carrier candidates are not arbitrary bond edges but seam-like
motif edges embedded in the cage topology.
```

Cautious bridge interpretation:

```text
In the controlled C60 object, geometry-readable relational information appears
to concentrate in specific motif/topology roles rather than being uniformly
distributed over all pair relations.
```

Internal image:

```text
Nicht jeder Faden trägt gleich.
Die H-H-Nähte sind die stärkeren Lastfäden.
```

---

## 12. Needed FU02b hardening

Because FU02-v0 labels all 90 edges as carriers, the next hardening step should sharpen the classifier.

Recommended FU02b:

```text
BMS-FU02b — Carrier Sharpness and Rank-Stability Extension
```

Add:

```text
1. percentile ranks for load_bearing_score
2. top-k carrier thresholds, e.g. top 10, top 20, top 30
3. motif enrichment tests for top-k sets
4. bootstrap or seed sensitivity if available
5. separate topology-only carrier score from weighted score
6. decoy-penalized carrier score
7. explicit graph_distance_shell reconstruction rather than skipping shells
```

Recommended sharper score:

```text
L_sharp(e) =
  mean_positive_delta_topology_reps(e)
  - max(core_seeded_decoy_retention(e), edge_class_shuffle_retention(e))
```

or:

```text
L_decoy_penalized(e) =
  P_real_retained(e)
  - max_N P_null_retained(e)
```

This would turn FU02 from:

```text
broad carrier-positive ranking
```

into:

```text
sharp carrier discrimination.
```

---

## 13. Result statement

Allowed:

```text
BMS-FU02-v0 identifies a ranked load-bearing pattern structure in the C60
diagnostic outputs. The strongest carrier candidates concentrate in H-H / 6:6
seam edges and associated local node neighborhoods, and they remain visible in
topology-only and graph-distance representations. Because the v0 labeling rule
marks all 90 bond edges as candidate carriers, the result should be interpreted
as a ranking and motif-contrast result rather than as a sharp classifier.
```

Short version:

```text
FU02-v0 shows that the whole C60 bond graph participates, but H-H / 6:6 seams
carry the strongest load-bearing signal.
```

Not allowed:

```text
All C60 edges are equally important.
Global C60 symmetry has been fully recovered.
The carrier edges are physical spacetime atoms.
C60 proves emergent spacetime.
```

---

## 14. Internal summary

```text
FU01:
  Eine Naht war echt.

FU01b:
  Andere Nähte tragen auch.

FU01c:
  Ohne farbige Nähte trägt der Ball immer noch.

FU02-v0:
  Der ganze Ball beteiligt sich,
  aber die H-H / 6:6-Nähte tragen am stärksten.

Grenze:
  v0 ist noch Ranking, kein scharfer Träger-Klassifikator.
```

---

## 15. Commit plan

Copy result note:

```bash
cd ~/Downloads/deBroglie_Kaster_Theorie/quantum-spacetime-bridge

cp ~/Downloads/BMS_FU02_LOAD_BEARING_PATTERN_INITIAL_RESULT_NOTE.md \
  docs/BMS_FU02_LOAD_BEARING_PATTERN_INITIAL_RESULT_NOTE.md

git status --short
```

Commit implementation and result note:

```bash
git add \
  data/bms_fu02_load_bearing_pattern_config.yaml \
  scripts/run_bms_fu02_load_bearing_pattern_analysis.py \
  docs/BMS_FU02_RUNNER_FIELD_LIST.md \
  docs/BMS_FU02_LOAD_BEARING_PATTERN_ANALYSIS_SPEC.md \
  docs/BMS_FU02_LOAD_BEARING_PATTERN_INITIAL_RESULT_NOTE.md

git status --short

git commit -m "Add BMS-FU02 load-bearing pattern analysis diagnostic"

git push
```
