# BMS-FU02c — Representation-Resolved Carrier Delta Extension Specification

Date: 2026-05-02  
Project: Gravitation und RaumZeit / Quantum-Spacetime-Bridge  
Recommended repo target: `docs/BMS_FU02C_REPRESENTATION_RESOLVED_CARRIER_DELTA_SPEC.md`  
Status: Specification and implementation block

## 1. Purpose

BMS-FU02c follows BMS-FU02b.

FU02b showed that under composite sharpness and decoy-penalized scoring the
top-ranked C60 carrier set is completely enriched for H,H / 6:6 seam edges.

FU02c asks:

```text
Sind H,H / 6:6 in jeder Brille Lastfäden?
```

The three tested representations are:

```text
bond_class_weighted
topology_only_equal_weight
graph_distance_similarity_d3
```

Scientific formulation:

```text
Do H,H / 6:6 seam edges remain the dominant carrier class when carrier deltas
are recomputed separately for each C60 representation?
```

## 2. Motivation

FU02b-v0 used FU02 aggregate persistence fields for the topology-sensitive
score. FU02c closes that scope gap by recomputing edge-level carrier deltas
directly from FU01c object-level edge inventories, separately by representation.

This moves from:

```text
aggregate topology-sensitive proxy
```

to:

```text
per-representation carrier delta table
```

## 3. Inputs

Primary FU01c outputs:

```text
runs/BMS-FU01c/c60_motif_topology_extension_open/bms_fu01c_edges.csv
runs/BMS-FU01c/c60_motif_topology_extension_open/bms_fu01c_real_vs_null_summary.csv
runs/BMS-FU01c/c60_motif_topology_extension_open/bms_fu01c_run_manifest.json
runs/BMS-FU01c/c60_motif_topology_extension_open/bms_fu01c_warnings.json
```

C60 audit inputs:

```text
data/bms_fu01_c60_edges.csv
data/bms_fu01_c60_nodes.csv
data/bms_fu01_c60_faces.csv
data/bms_fu01_c60_graph_manifest.json
```

## 4. Scope

FU02c-v0 reconstructs selected bond-edge envelopes for deterministic construction families:

```text
maximum_spanning_tree
mutual_knn
threshold
top_strength
```

`graph_distance_shells` is skipped by default unless a later explicitly
documented shell-anchor rule is added.

Project rule:

```text
lieber eine explizite Lücke als eine versteckte Rekonstruktion.
```

## 5. Core metric

For each edge and context:

```text
delta_edge =
  I(edge in real_selected_edges)
  - mean_k I(edge in null_selected_edges_k)
```

Representation-level aggregate:

```text
mean_delta_by_representation(edge, representation)
```

Conservative decoy/strong-null readout:

```text
min_delta_across_nulls(edge, representation)
```

This is positive only if the edge beats all tested null families on average
within that representation.

## 6. Expected outputs

```text
runs/BMS-FU02c/representation_resolved_carrier_delta_open/bms_fu02c_representation_edge_deltas.csv
runs/BMS-FU02c/representation_resolved_carrier_delta_open/bms_fu02c_edge_representation_summary.csv
runs/BMS-FU02c/representation_resolved_carrier_delta_open/bms_fu02c_representation_motif_enrichment.csv
runs/BMS-FU02c/representation_resolved_carrier_delta_open/bms_fu02c_consensus_carriers.csv
runs/BMS-FU02c/representation_resolved_carrier_delta_open/bms_fu02c_representation_rank_matrix.csv
runs/BMS-FU02c/representation_resolved_carrier_delta_open/bms_fu02c_run_manifest.json
runs/BMS-FU02c/representation_resolved_carrier_delta_open/bms_fu02c_warnings.json
runs/BMS-FU02c/representation_resolved_carrier_delta_open/bms_fu02c_config_resolved.yaml
```

## 7. Claim boundary

Allowed:

```text
BMS-FU02c tests whether the FU02b H,H / 6:6 seam dominance persists when
carrier deltas are recomputed separately for each representation.
```

Not allowed:

```text
Global C60 symmetry has been recovered.
The carriers are physical spacetime atoms.
A physical metric has been recovered.
C60 proves emergent spacetime.
```

## 8. Bridge relevance

FU02c asks whether the strongest current C60 structure-carrier class is stable
across representational lenses:

```text
weighted bond-class lens
topology-only lens
graph-distance lens
```

Internal formulation:

```text
Wenn H-H in jeder Brille trägt,
ist das kein Farbfleck auf der Linse.
Dann sitzt der Lastfaden im Gewebe.
```
