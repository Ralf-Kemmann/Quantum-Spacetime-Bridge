# BMS-FU02c — Representation-Resolved Carrier Delta Initial Result Note

Date: 2026-05-02  
Project: Gravitation und RaumZeit / Quantum-Spacetime-Bridge  
Recommended repo target: `docs/BMS_FU02C_REPRESENTATION_RESOLVED_CARRIER_DELTA_INITIAL_RESULT_NOTE.md`  
Status: Initial result note for BMS-FU02c-v0

---

## 1. Purpose

BMS-FU02c follows BMS-FU02b.

FU02b established a sharp carrier result:

```text
Under composite sharpness and decoy-penalized scoring, the top-ranked C60
carrier set is completely enriched for H,H / 6:6 seam edges.
```

FU02c asks the stricter representation-resolved question:

```text
Sind H,H / 6:6 in jeder Brille Lastfäden?
```

Representations:

```text
bond_class_weighted
topology_only_equal_weight
graph_distance_similarity_d3
```

---

## 2. Run manifest

Run:

```text
BMS-FU02c_representation_resolved_carrier_delta_open
```

Output directory:

```text
runs/BMS-FU02c/representation_resolved_carrier_delta_open
```

Core manifest values:

```json
{
  "c60_valid": true,
  "consensus_carrier_count": 90,
  "context_delta_row_count": 77760,
  "edge_representation_summary_row_count": 270,
  "fu01c_run_id": "BMS-FU01c_c60_motif_topology_extension_open",
  "fu01c_warning_count": 0,
  "representations": [
    "bond_class_weighted",
    "topology_only_equal_weight",
    "graph_distance_similarity_d3"
  ],
  "row_counts": {
    "consensus_carriers": 90,
    "edge_representation_summary": 270,
    "representation_edge_deltas": 77760,
    "representation_motif_enrichment": 18,
    "representation_rank_matrix": 90,
    "warnings": 2
  }
}
```

Warnings:

```text
info - FU02c-v0 skipped 144 graph_distance_shells contexts; shell reconstruction is not enabled.
info - FU02c-v0 used 864 non-shell representation-resolved contexts.
```

Interpretation of warnings:

```text
These warnings are expected and methodological, not data-failure warnings.
FU02c-v0 intentionally skips graph_distance_shells to avoid hidden shell
reconstruction assumptions.
```

---

## 3. Main result

FU02c gives a mixed but highly informative result.

The strong FU02b statement:

```text
H,H / 6:6 dominates the sharp carrier set.
```

is confirmed only for the `bond_class_weighted` representation.

In the topology-only and graph-distance representations, the top mean-delta carrier sets are dominated by H,P / 5:6 boundary edges.

Thus the simple strong hypothesis:

```text
H,H / 6:6 are the top carriers in every representation.
```

is not supported by FU02c-v0.

The better statement is:

```text
FU02c separates two carrier roles:
  1. H,H / 6:6 dominates the bond-class-weighted seam layer.
  2. H,P / 5:6 boundary edges dominate the topology-only and graph-distance
     mean-delta layers.
```

Internal short version:

```text
Nicht eine Lastfaden-Sorte in jeder Brille.
Sondern zwei Rollen:
  H-H trägt die Naht-/Bond-Class-Schicht.
  H-P trägt die topology-/distance-Boundary-Schicht.
```

---

## 4. Representation-resolved motif enrichment

### 4.1 Bond-class-weighted representation

Top 30 by `mean_delta_all_nulls`:

```text
H,H = 30
H,P = 0
H,H fraction = 1.0
H,H enrichment = 3.0
```

Top 30 by `min_delta_across_nulls`:

```text
H,H = 30
H,P = 0
H,H fraction = 1.0
H,H enrichment = 3.0
```

Interpretation:

```text
In the bond-class-weighted representation, FU02b's H,H / 6:6 seam dominance is
fully retained.
```

Top 10 by mean delta:

```text
1  c60_035--c60_056  H,H  mean_delta=0.6588888888888889  min_delta=0.3277777777777778
2  c60_033--c60_038  H,H  mean_delta=0.6495833333333334  min_delta=0.33111111111111113
3  c60_030--c60_052  H,H  mean_delta=0.6490277777777778  min_delta=0.31777777777777777
4  c60_039--c60_043  H,H  mean_delta=0.6445138888888889  min_delta=0.30388888888888893
5  c60_029--c60_047  H,H  mean_delta=0.6440277777777778  min_delta=0.2611111111111111
6  c60_034--c60_053  H,H  mean_delta=0.6330555555555556  min_delta=0.2538888888888889
7  c60_044--c60_048  H,H  mean_delta=0.6252777777777778  min_delta=0.26083333333333336
8  c60_040--c60_057  H,H  mean_delta=0.6227777777777778  min_delta=0.24638888888888888
9  c60_049--c60_054  H,H  mean_delta=0.6219444444444444  min_delta=0.27805555555555556
10 c60_018--c60_022  H,H  mean_delta=0.6159722222222221  min_delta=0.3088888888888889
```

Important detail:

```text
The bond-class-weighted H,H dominance also survives the conservative
min-delta / max-null-like penalty.
```

---

### 4.2 Topology-only equal-weight representation

Top 30 by `mean_delta_all_nulls`:

```text
H,H = 7
H,P = 23
H,H fraction = 0.23333333333333334
H,H enrichment = 0.7000000000000001
```

Top 30 by `min_delta_across_nulls`:

```text
H,H = 12
H,P = 18
H,H fraction = 0.4
H,H enrichment = 1.2000000000000002
```

Top 10 by mean delta:

```text
1  c60_057--c60_058  H,P  mean_delta=0.48375
2  c60_054--c60_055  H,P  mean_delta=0.48125000000000007
3  c60_052--c60_054  H,P  mean_delta=0.47750000000000004
4  c60_056--c60_060  H,P  mean_delta=0.475
5  c60_051--c60_053  H,P  mean_delta=0.4713194444444445
6  c60_058--c60_059  H,P  mean_delta=0.47
7  c60_059--c60_060  H,P  mean_delta=0.47
8  c60_051--c60_052  H,P  mean_delta=0.4509722222222222
9  c60_056--c60_057  H,P  mean_delta=0.44847222222222227
10 c60_050--c60_059  H,H  mean_delta=0.44729166666666664
```

Interpretation:

```text
When explicit bond-class weighting is removed, the leading mean-delta carrier
role shifts from H,H / 6:6 seam edges to H,P / 5:6 pentagon-boundary edges.
```

This is not a failure. It is a role separation:

```text
H,H carries the weighted seam role.
H,P carries a topology-only boundary role.
```

---

### 4.3 Graph-distance similarity representation

Top 30 by `mean_delta_all_nulls`:

```text
H,H = 7
H,P = 23
H,H fraction = 0.23333333333333334
H,H enrichment = 0.7000000000000001
```

Top 30 by `min_delta_across_nulls`:

```text
H,H = 12
H,P = 18
H,H fraction = 0.4
H,H enrichment = 1.2000000000000002
```

Top 10 by mean delta:

```text
1  c60_057--c60_058  H,P  mean_delta=0.349375
2  c60_054--c60_055  H,P  mean_delta=0.3475694444444445
3  c60_052--c60_054  H,P  mean_delta=0.3448611111111111
4  c60_056--c60_060  H,P  mean_delta=0.34305555555555556
5  c60_051--c60_053  H,P  mean_delta=0.3404166666666667
6  c60_058--c60_059  H,P  mean_delta=0.33944444444444444
7  c60_059--c60_060  H,P  mean_delta=0.33944444444444444
8  c60_051--c60_052  H,P  mean_delta=0.3179861111111111
9  c60_056--c60_057  H,P  mean_delta=0.3161805555555556
10 c60_050--c60_059  H,H  mean_delta=0.3153472222222222
```

Interpretation:

```text
The graph-distance representation closely mirrors the topology-only result:
H,P / 5:6 boundary edges dominate the top mean-delta ranks, while a smaller H,H
subset remains in the top 30.
```

This indicates:

```text
Topology-only and graph-distance readouts are detecting a boundary/interface
role rather than the same seam-role emphasized by bond-class weighting.
```

---

## 5. Consensus carriers

Consensus label counts:

```text
hh_consensus_all_representations: 7
hp_secondary_carrier: 23
representation_specific_candidate: 23
decoy_reproduced_or_unstable: 37
```

Interpretation:

```text
Only 7 H,H / 6:6 edges remain top-30 carriers in all three representations.
These are the strongest representation-consensus H,H candidates.
```

The 7 `hh_consensus_all_representations` edges are:

```text
c60_050--c60_059
c60_044--c60_048
c60_045--c60_058
c60_055--c60_060
c60_049--c60_054
c60_039--c60_043
c60_040--c60_057
```

These have:

```text
edge_type = 6_6
shared_face_types = H,H
top30_representations =
  bond_class_weighted
  graph_distance_similarity_d3
  topology_only_equal_weight
```

Interpretation:

```text
FU02c does not preserve all 30 H,H edges as all-representation carriers. It
selects a smaller seven-edge H,H consensus spine.
```

Internal short version:

```text
Nicht alle H-H-Nähte bleiben in jeder Brille oben.
Sieben H-H-Nähte bilden den Drei-Brillen-Kern.
```

---

## 6. H,P secondary carriers

FU02c identifies 23 `hp_secondary_carrier` edges.

These are top-30 in:

```text
topology_only_equal_weight
graph_distance_similarity_d3
```

but not in the bond-class-weighted top 30.

Examples:

```text
c60_054--c60_055
c60_059--c60_060
c60_057--c60_058
c60_052--c60_054
c60_051--c60_053
c60_056--c60_060
c60_058--c60_059
c60_053--c60_055
c60_046--c60_048
c60_049--c60_050
```

Interpretation:

```text
H,P / 5:6 edges act as topology/distance-sensitive secondary carriers.
```

This is an important refinement:

```text
H,P edges are not simply weak or irrelevant. They become prominent once the
explicit 6:6 / 5:6 bond-class weighting is removed.
```

Internal image:

```text
H-H sind die starken Nähte.
H-P sind die Grenz- und Umlenkstellen im Käfig.
```

---

## 7. Decoy/min-delta caution

In the topology-only and graph-distance top mean-delta lists, many top edges have:

```text
min_delta = 0.0
```

In consensus output, the 7 H,H all-representation carriers have:

```text
min_decoy_delta_across_representations = 0.0
```

The H,P secondary carriers often have:

```text
min_decoy_delta_across_representations < 0
```

Examples:

```text
c60_054--c60_055  H,P  min_decoy_delta=-0.10222222222222221
c60_059--c60_060  H,P  min_decoy_delta=-0.11472222222222223
c60_057--c60_058  H,P  min_decoy_delta=-0.1527777777777778
```

Interpretation:

```text
The topology/distance carrier roles are mean-delta positive but not robustly
positive under the strictest null-family penalty.
```

Therefore:

```text
FU02c supports representation-resolved role separation, but not a strong
all-null-decoy-penalized carrier proof for topology/distance roles.
```

This is a boundary, not a bug.

---

## 8. Comparison to FU02b

FU02b result:

```text
Composite sharpness top 30:
  H,H = 30
  H,P = 0
```

FU02c result:

```text
bond_class_weighted top 30:
  H,H = 30
  H,P = 0

topology_only_equal_weight top 30:
  H,H = 7
  H,P = 23

graph_distance_similarity_d3 top 30:
  H,H = 7
  H,P = 23
```

Thus FU02c shows that FU02b's H,H dominance is partly driven by the bond-class-weighted carrier layer.

But FU02c also preserves a nontrivial H,H consensus subset:

```text
7 H,H edges remain top-30 in all three representations.
```

Better conclusion:

```text
FU02b's broad H,H dominance is representation-dependent, while a smaller H,H
consensus spine survives representation separation.
```

This is more nuanced and more scientifically useful than a simple confirmation.

---

## 9. Bridge interpretation

Bridge-facing cautious statement:

```text
BMS-FU02c refines the FU02b carrier result by separating representation-specific
carrier roles. H,H / 6:6 seam edges dominate the bond-class-weighted
representation and form a seven-edge all-representation consensus subset.
However, topology-only and graph-distance representations shift their strongest
mean-delta carrier roles toward H,P / 5:6 boundary edges. This indicates that
geometry-readable relational structure is role-dependent: seam-like and
boundary-like carrier classes become prominent under different representational
lenses.
```

Short internal statement:

```text
Es gibt nicht nur einen Lastfaden.
Es gibt Naht-Träger und Grenz-Träger.
```

Bridge relevance:

```text
The Bridge should not expect one universal carrier class to dominate every
readout. Instead, different relational roles may contribute different kinds of
geometry-readable information.
```

This is actually stronger conceptually:

```text
Relational information has role structure, and the role depends on the
representation/lens through which geometry is read.
```

---

## 10. What FU02c does NOT prove

FU02c does not prove:

```text
global C60 symmetry recovery
physical spacetime geometry
a physical metric
molecular recognition
quantum chemistry
that carrier edges are physical spacetime atoms
```

FU02c also does not fully include:

```text
graph_distance_shells contexts
explicit shell-anchor reconstruction
true fullerene-preserving nulls
global cage-level symmetry diagnostics
spectral degeneracy analysis
```

Important scope boundary:

```text
FU02c-v0 computes representation-resolved non-shell carrier deltas and skips
graph_distance_shells contexts.
```

---

## 11. Result statement

Allowed:

```text
BMS-FU02c shows that the FU02b H,H / 6:6 carrier dominance is
representation-dependent. It is fully retained in the bond-class-weighted
representation, where the top 30 carriers are all H,H / 6:6. In contrast,
topology-only and graph-distance representations shift their strongest
mean-delta carrier ranks toward H,P / 5:6 boundary edges. A smaller seven-edge
H,H subset remains top-30 across all three representations, forming an
all-representation H,H consensus spine.
```

Short version:

```text
FU02c turns the FU02b result from one sharp H-H story into a two-role story:
H-H seams dominate the weighted seam layer, while H-P boundaries dominate the
topology/distance layer. Seven H-H edges survive as three-representation
consensus carriers.
```

Not allowed:

```text
H,H dominates every representation.
H,P is irrelevant.
Global C60 symmetry has been recovered.
A physical spacetime metric has been recovered.
```

---

## 12. Recommended next block

Recommended next block:

```text
BMS-FU02d — Carrier Role Geometry and Patch Distribution
```

Purpose:

```text
Map the seven H,H consensus carriers and the H,P secondary carriers across the
C60 cage to test whether they form patches, paths, seams, shells, or distributed
cage-level patterns.
```

Key questions:

```text
1. Are the seven H,H consensus carriers local or distributed?
2. Are H,P secondary carriers adjacent to the H,H consensus spine?
3. Do H,P carriers form boundary rings around H,H seam patches?
4. Do consensus carriers concentrate around specific faces or graph-distance shells?
5. Are the topology/distance H,P carriers explaining transitions between H,H seam
   neighborhoods?
```

Alternative next block:

```text
BMS-FU02c2 — Graph-Distance-Shell Reconstruction Extension
```

Purpose:

```text
Implement explicit graph_distance_shells reconstruction with documented anchor
rules and rerun FU02c including shell contexts.
```

Suggested order:

```text
First FU02d:
  understand carrier geometry / patch distribution.

Then FU02c2:
  add graph-distance shell reconstruction if needed.
```

---

## 13. Internal summary

```text
FU02b:
  H-H sind die Lastfäden.

FU02c:
  Nicht in jeder Brille gleich.

  bond_class_weighted:
    H-H dominiert vollständig.

  topology_only / graph_distance:
    H-P Boundary-Kanten dominieren die Mean-Delta-Spitze.

  all-representation consensus:
    7 H-H-Kanten bleiben als Drei-Brillen-Kern.

Kern:
  Es gibt Naht-Träger und Grenz-Träger.

Grenze:
  Kein globaler Käfigbeweis.
  Keine physikalische Raumzeit.
  Aber eine deutlich bessere Rollenkarte der relationalen Strukturträger.
```

---

## 14. Commit plan

Copy result note:

```bash
cd ~/Downloads/deBroglie_Kaster_Theorie/quantum-spacetime-bridge

cp ~/Downloads/BMS_FU02C_REPRESENTATION_RESOLVED_CARRIER_DELTA_INITIAL_RESULT_NOTE.md \
  docs/BMS_FU02C_REPRESENTATION_RESOLVED_CARRIER_DELTA_INITIAL_RESULT_NOTE.md

git status --short
```

Commit FU02c result note:

```bash
git add docs/BMS_FU02C_REPRESENTATION_RESOLVED_CARRIER_DELTA_INITIAL_RESULT_NOTE.md

git status --short

git commit -m "Add BMS-FU02c representation-resolved carrier result note"

git push
```
