# BMS-FU02b — Carrier Sharpness and Rank-Stability Initial Result Note

Date: 2026-05-02  
Project: Gravitation und RaumZeit / Quantum-Spacetime-Bridge  
Recommended repo target: `docs/BMS_FU02B_CARRIER_SHARPNESS_INITIAL_RESULT_NOTE.md`  
Status: Initial result note for BMS-FU02b-v0

---

## 1. Purpose

BMS-FU02b follows BMS-FU02-v0.

FU02-v0 showed:

```text
The whole C60 bond graph participates in the broad load-bearing score, but
H,H / 6:6 seam edges carry the strongest average signal.
```

FU02b asks the sharper question:

```text
Welche Träger bleiben oben, wenn Rankingdruck und Decoy-Strafe dazukommen?
```

Scientific formulation:

```text
Which C60 carrier candidates remain top-ranked under sharpness scoring,
decoy-penalized scoring, topology-sensitive scoring and motif-enrichment
analysis?
```

Internal image:

```text
FU02-v0:
  Der ganze Ball beteiligt sich.

FU02b:
  Jetzt sehen wir, welche Lastfäden wirklich oben bleiben.
```

---

## 2. Main result

BMS-FU02b gives a clear sharpening result.

The top 30 edges by `sharpness_score` are all:

```text
edge_type = 6_6
shared_face_types = H,H
```

Thus:

```text
sharpness_score top_30:
  H,H = 30
  H,P = 0
  H,H fraction = 1.0
  H,H enrichment = 3.0
```

This is the decisive FU02b result:

```text
Under sharpness scoring, the sharp carrier set collapses onto the complete
H,H / 6:6 seam class.
```

Internal short version:

```text
Unter Rankingdruck bleiben die H-H-Nähte oben.
```

---

## 3. Top sharpness carriers

Top 10 by `sharpness_score`:

```text
1  c60_018--c60_022  6_6  H,H  sharp=0.8426966292134832
2  c60_030--c60_052  6_6  H,H  sharp=0.8415730337078651
3  c60_020--c60_041  6_6  H,H  sharp=0.8393258426966292
4  c60_035--c60_056  6_6  H,H  sharp=0.8376404494382023
5  c60_033--c60_038  6_6  H,H  sharp=0.8280898876404493
6  c60_025--c60_046  6_6  H,H  sharp=0.8202247191011236
7  c60_014--c60_032  6_6  H,H  sharp=0.8174157303370786
8  c60_039--c60_043  6_6  H,H  sharp=0.8174157303370786
9  c60_023--c60_028  6_6  H,H  sharp=0.8140449438202247
10 c60_019--c60_037  6_6  H,H  sharp=0.8056179775280897
```

Interpretation:

```text
The sharpest load-bearing carrier candidates are all hexagon-hexagon seam
edges.
```

This is stronger than FU02-v0, because FU02-v0 labeled all 90 edges broadly positive, while FU02b reveals that the highest-ranked sharp carrier layer is entirely H,H / 6:6.

---

## 4. Motif enrichment

### 4.1 Decoy-penalized score

```text
score_decoy_penalized top_10:
  H,H = 10
  H,P = 0
  H,H fraction = 1.0
  H,H enrichment = 3.0

score_decoy_penalized top_20:
  H,H = 20
  H,P = 0
  H,H fraction = 1.0
  H,H enrichment = 3.0

score_decoy_penalized top_30:
  H,H = 30
  H,P = 0
  H,H fraction = 1.0
  H,H enrichment = 3.0
```

Interpretation:

```text
After penalizing by the strongest tested null reproduction channel, the entire
top 30 remains H,H / 6:6.
```

This means:

```text
The sharp H,H seam enrichment is not removed by max-null / decoy penalty.
```

---

### 4.2 Topology-sensitive score

```text
score_topology_sensitive top_10:
  H,H = 10
  H,P = 0
  H,H fraction = 1.0
  H,H enrichment = 3.0

score_topology_sensitive top_20:
  H,H = 19
  H,P = 1
  H,H fraction = 0.95
  H,H enrichment = 2.85

score_topology_sensitive top_30:
  H,H = 27
  H,P = 3
  H,H fraction = 0.9
  H,H enrichment = 2.7
```

Interpretation:

```text
The topology-sensitive score also strongly enriches H,H / 6:6 seams, but it
allows a small number of H,P / 5:6 boundary edges into the top 20 and top 30.
```

This is important:

```text
The topology-sensitive view is not exclusively H,H, but remains strongly H,H
dominated.
```

---

### 4.3 Composite sharpness score

```text
sharpness_score top_10:
  H,H = 10
  H,P = 0
  H,H fraction = 1.0
  H,H enrichment = 3.0

sharpness_score top_20:
  H,H = 20
  H,P = 0
  H,H fraction = 1.0
  H,H enrichment = 3.0

sharpness_score top_30:
  H,H = 30
  H,P = 0
  H,H fraction = 1.0
  H,H enrichment = 3.0
```

Interpretation:

```text
The composite sharpness score cleanly separates the H,H / 6:6 seam class as the
dominant sharp carrier class.
```

Internal image:

```text
Wenn man die Attrappen abzieht und die Ränge schärft,
bleiben die Hexagon-Hexagon-Nähte oben.
```

---

## 5. Candidate labels

The top 20 by `sharpness_score` are labeled:

```text
sharp_hh_seam_carrier
```

Ranks 21–22 and 29 are:

```text
sharp_topology_carrier
```

but still have:

```text
edge_type = 6_6
shared_face_types = H,H
```

Several lower top-30 H,H edges are:

```text
decoy_penalized_survivor
```

Interpretation:

```text
Even the less strongly labeled top-30 edges remain H,H / 6:6. The label change
reflects stricter rule thresholds, not a motif change.
```

---

## 6. Decoy-penalized interpretation

FU02b uses:

```text
score_decoy_penalized =
  real_retention_rate - max_null_retention_rate
```

This means each edge is compared against the strongest tested null reproduction channel, not just the average null.

Top decoy-penalized H,H carriers include:

```text
c60_033--c60_038
c60_035--c60_056
c60_030--c60_052
c60_018--c60_022
c60_039--c60_043
c60_025--c60_046
c60_020--c60_041
c60_023--c60_028
c60_049--c60_054
c60_014--c60_032
```

Interpretation:

```text
The H,H enrichment survives the stricter max-null penalty.
```

This strengthens the FU02-v0 motif result.

---

## 7. Topology-sensitive interpretation

Top topology-sensitive edges are also heavily H,H dominated:

```text
top_10: 10 H,H / 0 H,P
top_20: 19 H,H / 1 H,P
top_30: 27 H,H / 3 H,P
```

The first H,P edge in the topology-sensitive top 20 is:

```text
c60_054--c60_055
```

This suggests:

```text
Some H,P / 5:6 boundary edges can participate in topology-sensitive structure,
but they are not the leading sharp carrier class.
```

Defensive interpretation:

```text
FU02b does not exclude pentagon-boundary participation. It shows that, under
the current sharpness definitions, H,H / 6:6 seams dominate the sharp carrier
layer.
```

---

## 8. Node-level sharp neighborhoods

Top node neighborhoods by mean incident sharpness include:

```text
c60_054
c60_055
c60_049
c60_059
c60_053
c60_014
c60_050
c60_008
c60_060
c60_034
```

The top node:

```text
c60_054
  mean_incident_sharpness_score = 0.600936329588015
  top20_edges = 1
  top30_edges = 1
  incident labels:
    decoy_reproduced_candidate: 1
    sharp_hh_seam_carrier: 1
    sharp_topology_carrier: 1
```

Interpretation:

```text
Sharp carrier edges cluster into local node neighborhoods. The top nodes are
not merely endpoints of one exceptional edge; they sit at junctions where sharp
H,H seam edges and topology-sensitive boundary edges meet.
```

Internal image:

```text
Die Lastfäden bilden kleine Knotenpunkte im Gewebe.
```

---

## 9. What FU02b adds beyond FU02-v0

FU02-v0:

```text
All 90 C60 bond edges are broadly carrier-positive.
H,H has a stronger mean score than H,P.
```

FU02b:

```text
Top 10 / top 20 / top 30 by decoy-penalized and composite sharpness scores are
entirely H,H / 6:6.

Topology-sensitive top sets are also strongly H,H enriched, though not
exclusively H,H beyond top 10.
```

Thus FU02b turns the FU02-v0 result from:

```text
broad participation with H,H advantage
```

into:

```text
sharp H,H / 6:6 seam dominance under ranking pressure and decoy penalty.
```

---

## 10. Bridge interpretation

Bridge-facing cautious statement:

```text
BMS-FU02b sharpens the C60 load-bearing pattern result. Under composite
sharpness and decoy-penalized scoring, the top-ranked carrier set is completely
enriched for H,H / 6:6 seam edges. This supports the interpretation that
geometry-readable relational structure is not uniformly distributed over the
C60 bond graph, but concentrates in specific motif/topology roles. The result
remains a controlled graph-diagnostic finding and should not be interpreted as
a physical spacetime or molecular-recognition proof.
```

Short internal statement:

```text
Nicht alle Fäden tragen gleich.
Die H-H-Nähte sind die Lastfäden.
```

Relation to Bridge principle:

```text
A relation becomes Bridge-relevant not by existing, but by retaining a
distinguishable structural role under transformations and null contrasts.
```

FU02b supports that:

```text
The H,H / 6:6 seam class is the strongest current candidate for such a
structural role in the C60 calibration object.
```

---

## 11. What FU02b does NOT prove

FU02b does not prove:

```text
global C60 symmetry recovery
physical spacetime geometry
a physical metric
molecular recognition
quantum chemistry
that H,H seams are physical spacetime atoms
```

FU02b also does not fully resolve:

```text
representation-specific carrier deltas at context level
true fullerene-preserving nulls
global cage-level organization
spectral degeneracy / symmetry effects
```

Important scope boundary:

```text
FU02b-v0 topology-sensitive score uses FU02 aggregate persistence fields. It
does not fully recompute representation-specific edge deltas from FU01c
contexts.
```

Therefore:

```text
FU02b-v0 is a sharpness/ranking result, not a final representation-resolved
carrier proof.
```

---

## 12. Open questions

1. Are the top H,H seam edges spatially distributed across the C60 cage or concentrated in particular patches?

2. Do top H,H carriers map to special shortest-path / shell roles?

3. Do top H,H carriers remain sharp under full representation-specific recomputation?

4. Do true fullerene-preserving nulls reproduce the H,H dominance?

5. Do spectral or cycle-depth features explain why the H,H seam class dominates?

6. Are the few topology-sensitive H,P boundary edges bridge-like secondary carriers?

---

## 13. Recommended next block

Recommended next block:

```text
BMS-FU02c — Representation-Resolved Carrier Delta Extension
```

Purpose:

```text
Replace FU02b-v0's aggregate topology-sensitive proxy with full per-representation,
per-core, per-null edge-level deltas.
```

Recommended additions:

```text
1. recompute edge deltas separately for:
   - bond_class_weighted
   - topology_only_equal_weight
   - graph_distance_similarity_d3

2. compute carrier ranks per representation

3. compare H,H and H,P ranks per representation

4. check whether the H,H dominance remains after full representation-resolved
   recomputation

5. inspect graph_distance_shells contexts explicitly instead of skipping them
```

Alternative next block:

```text
BMS-FU02d — Carrier Geometry and Patch Distribution
```

Purpose:

```text
Map the top H,H carriers across the C60 cage to test whether they are globally
distributed, patch-local, shell-local or construction-tie driven.
```

---

## 14. Result statement

Allowed:

```text
BMS-FU02b sharpens the FU02-v0 carrier ranking. The top-ranked C60 carrier
candidates under composite sharpness and decoy-penalized scoring are entirely
H,H / 6:6 seam edges, with a threefold enrichment relative to the full C60 edge
baseline. Topology-sensitive ranking is also strongly H,H enriched, though it
admits a small number of H,P boundary edges beyond the top 10. This supports a
controlled motif/topology-role interpretation of the strongest load-bearing
patterns.
```

Short version:

```text
FU02b turns the broad FU02-v0 carrier-positive result into a sharp H,H / 6:6
seam dominance result.
```

Not allowed:

```text
Global C60 symmetry has been fully recovered.
The carrier edges are physical spacetime atoms.
C60 proves emergent spacetime.
A physical metric has been recovered.
```

---

## 15. Internal summary

```text
FU02-v0:
  Der ganze Ball beteiligt sich,
  aber H-H ist stärker.

FU02b:
  Unter Rankingdruck und Decoy-Strafe bleiben die H-H / 6:6-Nähte oben.

Kern:
  Nicht alle Fäden tragen gleich.
  Die H-H-Nähte sind die Lastfäden.

Grenze:
  Noch kein globaler Käfigbeweis.
  Noch keine physikalische Geometrie.
  Aber ein scharfer motif/topology carrier result.
```

---

## 16. Commit plan

Copy result note:

```bash
cd ~/Downloads/deBroglie_Kaster_Theorie/quantum-spacetime-bridge

cp ~/Downloads/BMS_FU02B_CARRIER_SHARPNESS_INITIAL_RESULT_NOTE.md \
  docs/BMS_FU02B_CARRIER_SHARPNESS_INITIAL_RESULT_NOTE.md

git status --short
```

Commit implementation and result note:

```bash
git add \
  data/bms_fu02b_carrier_sharpness_config.yaml \
  scripts/run_bms_fu02b_carrier_sharpness_rank_stability.py \
  docs/BMS_FU02B_RUNNER_FIELD_LIST.md \
  docs/BMS_FU02B_CARRIER_SHARPNESS_RANK_STABILITY_SPEC.md \
  docs/BMS_FU02B_CARRIER_SHARPNESS_INITIAL_RESULT_NOTE.md

git status --short

git commit -m "Add BMS-FU02b carrier sharpness rank stability diagnostic"

git push
```
