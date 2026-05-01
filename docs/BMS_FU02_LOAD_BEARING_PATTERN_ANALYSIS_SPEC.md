# BMS-FU02 — Load-Bearing Pattern Analysis Specification

Date: 2026-05-01  
Project: Gravitation und RaumZeit / Quantum-Spacetime-Bridge  
Recommended repo target: `docs/BMS_FU02_LOAD_BEARING_PATTERN_ANALYSIS_SPEC.md`  
Status: Specification only; no numerical run completed yet

---

## 1. Purpose

BMS-FU02 follows FU01/FU01b/FU01c.

The earlier FU blocks established:

```text
FU01:
  A local 6:6 seam is retained against degree-preserving rewires.

FU01b:
  Other local and distributed 6:6 / 5:6 core selections also carry signal.

FU01c:
  The signal does not collapse after removing explicit 6:6 / 5:6 edge weights.
  Topology-only and graph-distance representations retain real-over-null
  separation against topology-perturbing nulls.
```

BMS-FU02 asks the next question:

```text
Welche Muster tragen — und warum tragen sie?
```

Scientific formulation:

```text
Which local and relational graph patterns are repeatedly retained across
representations, core variants, construction rules and null families, and what
structural properties explain their stability?
```

Internal image:

```text
FU01c sagt:
  Ohne farbige Nähte trägt der Ball immer noch.

FU02 fragt:
  Welche Fäden halten das Gewebe zusammen?
```

---

## 2. Motivation

FU01c showed that C60 topology-sensitive signal persists beyond explicit edge-class weights.

However, FU01c does not yet explain why certain core edges or neighborhoods are retained.

The missing explanation layer is:

```text
load-bearing pattern analysis
```

This means moving from:

```text
This edge/core is retained.
```

to:

```text
This edge/core is retained because it has identifiable structural roles:
local face context, cycle embedding, shortest-path role, shell position,
redundancy, spectral contribution or cross-representation stability.
```

Bridge relevance:

```text
The Bridge should not treat all relations as equally informative. A relation is
Bridge-relevant only if it carries distinguishable, robust structure under
allowed transformations.
```

Internal principle:

```text
Tragend ist nicht, was groß aussieht.
Tragend ist, was unter erlaubten Transformationen unterscheidbar bleibt.
```

---

## 3. Working question

Main question:

```text
What common structural properties characterize the C60 patterns that remain
stable across FU01/FU01b/FU01c diagnostics?
```

Sub-questions:

```text
1. Which bond edges appear repeatedly in retained core/envelope patterns?

2. Which nodes appear repeatedly in retained core/envelope patterns?

3. Are retained edges biased toward 6:6 seams, 5:6 pentagon boundaries, or both?

4. Are retained edges close to particular face motifs?

5. Are retained edges embedded in many short cycles?

6. Do retained nodes/edges occupy special graph-distance or shell roles?

7. Do retained patterns contribute strongly to Laplacian or adjacency spectra?

8. Which retained patterns remain visible in topology-only and graph-distance
   representations?

9. Which retained patterns disappear under edge-class shuffle or core-seeded
   decoy?

10. Which patterns are true candidates for relational structure carriers?
```

---

## 4. Recommended block label

```text
BMS-FU02
```

Meaning:

```text
BMS = Bridge-readable Matter / Structure
FU  = Fullerene
02  = load-bearing pattern analysis after FU01 calibration series
```

Recommended output directory:

```text
runs/BMS-FU02/load_bearing_pattern_analysis_open/
```

Recommended repo files:

```text
docs/BMS_FU02_LOAD_BEARING_PATTERN_ANALYSIS_SPEC.md
docs/BMS_FU02_RUNNER_FIELD_LIST.md
docs/BMS_FU02_LOAD_BEARING_PATTERN_RESULT_NOTE.md

data/bms_fu02_load_bearing_pattern_config.yaml
scripts/run_bms_fu02_load_bearing_pattern_analysis.py
```

---

## 5. Input artifacts

Primary FU01c outputs:

```text
runs/BMS-FU01c/c60_motif_topology_extension_open/bms_fu01c_real_vs_null_summary.csv
runs/BMS-FU01c/c60_motif_topology_extension_open/bms_fu01c_envelope_metrics.csv
runs/BMS-FU01c/c60_motif_topology_extension_open/bms_fu01c_core_metrics.csv
runs/BMS-FU01c/c60_motif_topology_extension_open/bms_fu01c_edges.csv
runs/BMS-FU01c/c60_motif_topology_extension_open/bms_fu01c_reference_core_edges.csv
runs/BMS-FU01c/c60_motif_topology_extension_open/bms_fu01c_core_variants.csv
runs/BMS-FU01c/c60_motif_topology_extension_open/bms_fu01c_representations.csv
runs/BMS-FU01c/c60_motif_topology_extension_open/bms_fu01c_run_manifest.json
```

Primary C60 audit inputs:

```text
data/bms_fu01_c60_nodes.csv
data/bms_fu01_c60_edges.csv
data/bms_fu01_c60_faces.csv
data/bms_fu01_c60_graph_manifest.json
```

The runner should refuse or warn if:

```text
FU01c warnings != 0
C60 graph manifest does not report c60_valid = true
required FU01c output files are missing
```

---

## 6. Analysis levels

BMS-FU02 should analyze three levels.

### 6.1 Edge-level load-bearing score

For each C60 bond edge:

```text
How often does this edge appear in real retained envelopes across
representations, core variants and construction rules?
```

Candidate edge-level properties:

```text
edge_type
shared_face_types
shared_faces
local_face_signature
graph_distance role
cycle participation
shell position
null suppression strength
cross-representation persistence
```

### 6.2 Node-level load-bearing score

For each C60 node:

```text
How often does this node appear in retained patterns?
```

Candidate node-level properties:

```text
degree
incident edge types
incident face motifs
shortest-path centrality proxy
shell role from selected anchors
cycle participation proxy
cross-core persistence
```

### 6.3 Motif-level load-bearing score

For recurring local patterns:

```text
Which motifs are repeatedly retained?
```

Candidate motifs:

```text
6:6 H-H seam edge
5:6 H-P boundary edge
pentagon-adjacent neighborhood
hexagon seam chain
short cycle neighborhood
graph-distance shell patch
multi-core overlap patch
```

---

## 7. Core concept: load-bearing score

BMS-FU02 should define a conservative load-bearing score.

### 7.1 Edge load-bearing score

Recommended first-pass score:

```text
L_edge(e) =
  P_real_retained(e)
  - mean_N P_null_retained(e)
```

where:

```text
P_real_retained(e):
  fraction of selected real envelopes containing edge e

mean_N P_null_retained(e):
  mean fraction of selected null envelopes containing edge e
```

Compute separately by:

```text
representation_id
core_variant_id
construction_family
construction_variant
null_family
```

Then aggregate cautiously.

### 7.2 Cross-representation persistence

```text
X_edge(e) =
  number of representations in which e has positive real-over-null retention
```

Representations:

```text
bond_class_weighted
topology_only_equal_weight
graph_distance_similarity_d3
```

Interpretation:

```text
Edges with positive retention across all three representations are stronger
candidate structure carriers than edges retained only in the weighted variant.
```

### 7.3 Null-resistance profile

For each edge:

```text
N_edge(e) =
  {
    degree_preserving_rewire_delta,
    edge_class_shuffle_delta,
    motif_class_preserving_edge_swap_proxy_delta,
    core_seeded_decoy_delta
  }
```

Interpretation:

```text
A strong candidate should not only beat degree rewires. It should also be
understood relative to edge-class shuffle, motif proxy and core-seeded decoy.
```

### 7.4 Candidate structure-carrier label

Recommended labels:

```text
cross_representation_structure_carrier
topology_only_structure_carrier
weighted_only_candidate
decoy_reproducible_candidate
motif_proxy_reproducible_candidate
inconclusive_or_tie_sensitive
```

---

## 8. Structural explanatory features

For every edge and node, FU02 should compute explanatory features.

### 8.1 Edge features

| field name | type | description |
|---|---:|---|
| `edge_key` | string | Canonical edge id `source--target`. |
| `source` | string | Source node id. |
| `target` | string | Target node id. |
| `edge_type` | string | `6_6` or `5_6`. |
| `shared_faces` | string | Face ids incident to the edge. |
| `shared_face_types` | string | Face types incident to the edge, e.g. `H,H` or `H,P`. |
| `pentagon_incident` | bool | Whether edge touches a pentagon face. |
| `hexagon_hexagon_edge` | bool | Whether edge is a 6:6 H-H edge. |
| `local_face_signature` | string | Compact face signature. |
| `cycle5_proxy_count` | integer | Number of pentagon-face incidences. |
| `cycle6_proxy_count` | integer | Number of hexagon-face incidences. |
| `line_graph_degree` | integer | Number of adjacent edges sharing a node. |
| `edge_betweenness_proxy` | float | Shortest-path edge betweenness proxy if computed. |
| `mean_endpoint_shortest_path_centrality` | float | Mean endpoint closeness-like score. |
| `endpoint_shell_signature` | string | Shell placement from selected anchor(s). |

### 8.2 Node features

| field name | type | description |
|---|---:|---|
| `node_id` | string | C60 node id. |
| `degree` | integer | Node degree; expected 3. |
| `incident_6_6_count` | integer | Number of incident 6:6 edges. |
| `incident_5_6_count` | integer | Number of incident 5:6 edges. |
| `pentagon_membership_count` | integer | Number of incident pentagon faces; expected 1. |
| `hexagon_membership_count` | integer | Number of incident hexagon faces; expected 2. |
| `shortest_path_closeness_proxy` | float | Closeness-like centrality proxy. |
| `shell_signature` | string | Distance shell from selected anchor(s). |
| `retained_edge_incidence_count` | integer | Number of retained candidate edges incident to node. |

### 8.3 Spectral features

Optional first-pass spectral descriptors:

```text
adjacency eigenvector centrality proxy
Laplacian Fiedler vector value
local spectral contribution proxy
```

Caution:

```text
C60 is highly symmetric; many spectral quantities may be degenerate or
basis-sensitive. Use spectral features as diagnostics, not proof.
```

---

## 9. Recommended outputs

Recommended output directory:

```text
runs/BMS-FU02/load_bearing_pattern_analysis_open/
```

Expected files:

```text
bms_fu02_edge_load_bearing_scores.csv
bms_fu02_node_load_bearing_scores.csv
bms_fu02_motif_load_bearing_summary.csv
bms_fu02_edge_explanatory_features.csv
bms_fu02_node_explanatory_features.csv
bms_fu02_cross_representation_carriers.csv
bms_fu02_null_resistance_profiles.csv
bms_fu02_candidate_structure_carriers.csv
bms_fu02_run_manifest.json
bms_fu02_warnings.json
bms_fu02_config_resolved.yaml
```

Optional visual artifacts later:

```text
bms_fu02_edge_load_bearing_network_map.png
bms_fu02_node_load_bearing_network_map.png
bms_fu02_candidate_carrier_subgraph.png
```

---

## 10. Decision rules

### 10.1 Strong candidate structure carrier

An edge or motif may be labeled:

```text
cross_representation_structure_carrier
```

if it satisfies:

```text
1. positive real-over-null retention in at least two topology-sensitive
   representations, including topology_only_equal_weight or graph_distance_similarity_d3

2. positive retention against degree_preserving_rewire

3. not fully reproduced by core_seeded_decoy

4. not only present in bond_class_weighted representation
```

### 10.2 Topology-only carrier

Label:

```text
topology_only_structure_carrier
```

if:

```text
1. retained in topology_only_equal_weight
2. retained in graph_distance_similarity_d3
3. not dependent on explicit edge-class weights
```

### 10.3 Weighted-only candidate

Label:

```text
weighted_only_candidate
```

if:

```text
1. retained in bond_class_weighted
2. weak or absent in topology_only_equal_weight and graph_distance_similarity_d3
```

### 10.4 Decoy-reproducible candidate

Label:

```text
decoy_reproducible_candidate
```

if:

```text
core_seeded_decoy reproduces the retention behavior.
```

### 10.5 Motif-proxy reproducible candidate

Label:

```text
motif_proxy_reproducible_candidate
```

if:

```text
motif_class_preserving_edge_swap_proxy reproduces the retention behavior.
```

### 10.6 Inconclusive

Label:

```text
inconclusive_or_tie_sensitive
```

if:

```text
results are dominated by equal-weight ties, empty selections, inconclusive
summary rows, or construction artifacts.
```

---

## 11. Interpretation patterns

### Pattern A — carriers are mostly 6:6 H-H seams

Allowed interpretation:

```text
The retained C60 signal is concentrated in hexagon-hexagon seam structure.
```

### Pattern B — carriers include both 6:6 and 5:6

Allowed interpretation:

```text
Both hexagon-hexagon seams and pentagon-boundary edges contribute to the
load-bearing pattern set.
```

### Pattern C — topology-only carriers overlap weighted carriers

Allowed interpretation:

```text
Some load-bearing patterns are not merely weight-class artifacts; they remain
visible as topology-sensitive structure carriers.
```

### Pattern D — motif-proxy reproduces the carriers

Allowed interpretation:

```text
The carrier set is largely explained by local motif class rather than global
cage organization.
```

### Pattern E — motif-proxy does not reproduce carriers

Allowed interpretation:

```text
The carrier set may reflect broader organization beyond local edge-type class,
but stronger fullerene-preserving controls are needed.
```

---

## 12. Claim boundary

Allowed:

```text
BMS-FU02 analyzes which C60 edges, nodes and local motifs function as
load-bearing relational patterns across FU01c representations and null models.
```

Allowed after positive result:

```text
BMS-FU02 identifies candidate relational structure carriers whose retention is
not restricted to explicit edge-class weights.
```

Not allowed:

```text
C60 proves emergent spacetime.
The bridge recognizes molecules.
A physical metric has been recovered.
Global C60 symmetry has been fully recovered.
The identified carriers are physical spacetime atoms.
```

---

## 13. Bridge relevance

FU02 is important because it shifts the bridge discussion from:

```text
relations have values
```

to:

```text
relations have roles
```

Bridge-facing cautious statement:

```text
The load-bearing pattern analysis asks which relations retain distinguishable
structural roles under representation changes and null transformations. Such
relations are candidate carriers of geometry-readable information, but not yet
physical geometry themselves.
```

Internal formulation:

```text
Nicht jeder Faden in der Beziehungssuppe ist tragend.
Aber manche Fäden halten das Gewebe zusammen.
```

---

## 14. Recommended first runner scope

For FU02-v0, keep the scope controlled:

```text
1. Use FU01c outputs only.
2. Focus on edge-level and node-level load-bearing scores.
3. Include cross-representation persistence.
4. Include null-resistance profile.
5. Include simple explanatory features from C60 faces and graph distances.
6. Do not implement heavy spectral analysis in v0 unless the first pass is clean.
```

Recommended later FU02b:

```text
spectral and cycle-depth extension
```

---

## 15. Minimal commit plan

Commit this specification first:

```bash
cd ~/Downloads/deBroglie_Kaster_Theorie/quantum-spacetime-bridge

cp ~/Downloads/BMS_FU02_LOAD_BEARING_PATTERN_ANALYSIS_SPEC.md \
  docs/BMS_FU02_LOAD_BEARING_PATTERN_ANALYSIS_SPEC.md

git add docs/BMS_FU02_LOAD_BEARING_PATTERN_ANALYSIS_SPEC.md

git status --short

git commit -m "Add BMS-FU02 load-bearing pattern analysis specification"

git push
```

Implementation should follow only after this spec is reviewed.

---

## 16. Internal summary

```text
FU01:
  Eine Naht war echt.

FU01b:
  Andere Nähte tragen auch.

FU01c:
  Ohne farbige Nähte trägt der Ball immer noch.

FU02:
  Jetzt fragen wir:
    Welche Fäden tragen?
    Warum tragen sie?
    Sind sie nur Gewicht, nur Motiv, oder echte relationale Strukturträger?
```
