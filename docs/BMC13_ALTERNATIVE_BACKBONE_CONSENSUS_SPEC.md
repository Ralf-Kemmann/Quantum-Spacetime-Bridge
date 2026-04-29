# BMC-13 Alternative Backbone / Consensus-Backbone Filters Specification

## Purpose

BMC-13 addresses the main remaining methodological objection after BMC-12f:

```text
The current backbone variants may not be independent methods.
```

BMC-12f showed that the BMC09d reference anchor at N=81 is stable across the tested decision-threshold / dominance-gap grid.

However, the previous backbone variants are all members of the same top-strength family:

```text
strength_topk_6
strength_topalpha_025
strength_topalpha_050
```

These are different cuts through the same edge-weight ordering. Therefore, BMC-13 tests whether the N=81 anchor is visible under conceptually different backbone extraction rules.

---

## Working question

```text
Does the N=81 sparse/local backbone anchor persist when the backbone is extracted by alternative non-identical methods?
```

Internally:

```text
Bleibt der Kristallisationskeim sichtbar, wenn wir die Beleuchtung wechseln?
```

---

## Input

Primary input:

```text
runs/BMC-12e/edgecount_neighborhood_sweep_open/bmc12e_edgecount_sweep_edges_inventory.csv
```

BMC-13 initially focuses on:

```text
edge_count_target = 81
case_id = baseline_all_features
```

The N=81 all-feature graph is the current strongest reference point after BMC-12f.

---

## Methods in BMC-13 initial block

### 1. top_strength_reference

Reference family comparable to the previous top-strength logic.

Default:

```text
k_reference_edges = 6
```

### 2. mutual_kNN

A local-neighborhood method.

For each node, identify its top `k` strongest neighbors. Keep an edge only if both endpoints select each other.

Default:

```text
k = 3
```

### 3. maximum_spanning_tree

A global load-bearing skeleton.

Builds a maximum spanning tree from all available N=81 edges.

Interpretation:

```text
Keep a minimal connected high-weight scaffold.
```

### 4. threshold_path_consensus

A sparsity-path persistence method.

Uses BMC-12e baseline edge sets at:

```text
N = 70, 75, 81
```

and keeps edges that occur across all selected sparse-path levels.

---

## Core comparisons

For each method:

```text
edge_count
node_count
component_count
largest_component_size
overlap_with_reference_edges
jaccard_with_reference_edges
overlap_with_consensus_edges
jaccard_with_consensus_edges
mean_edge_weight
min_edge_weight
max_edge_weight
```

---

## Interpretation

### Strong method support

If multiple alternative methods overlap strongly with the reference backbone, this supports:

```text
method-crossing persistence of the N=81 local anchor
```

### Weak method support

If alternative methods produce very different skeletons, then the current BMC09d/BMC-12f anchor should be treated as:

```text
top-strength-method specific
```

This would not invalidate the earlier result, but it would narrow its interpretation.

---

## Outputs

BMC-13 writes:

```text
runs/BMC-13/alternative_backbone_consensus_open/bmc13_backbone_edges.csv
runs/BMC-13/alternative_backbone_consensus_open/bmc13_method_summary.csv
runs/BMC-13/alternative_backbone_consensus_open/bmc13_pairwise_overlap_summary.csv
runs/BMC-13/alternative_backbone_consensus_open/bmc13_readout.md
runs/BMC-13/alternative_backbone_consensus_open/bmc13_metrics.json
```

---

## Field list: bmc13_backbone_edges.csv

| field | type | description |
|---|---|---|
| method_id | string | Backbone extraction method |
| edge_count_target | integer | Source edge-count target |
| case_id | string | Source case ID |
| source | string | Source node |
| target | string | Target node |
| weight | float | Edge weight |
| edge_rank_in_source | integer | Rank by descending weight inside source edge set |
| selected_by_method | boolean string | Always true in this output |

---

## Field list: bmc13_method_summary.csv

| field | type | description |
|---|---|---|
| method_id | string | Backbone extraction method |
| edge_count | integer | Number of selected edges |
| node_count | integer | Number of participating nodes |
| component_count | integer | Number of connected components |
| largest_component_size | integer | Size of largest connected component |
| mean_edge_weight | float | Mean selected edge weight |
| min_edge_weight | float | Minimum selected edge weight |
| max_edge_weight | float | Maximum selected edge weight |
| overlap_with_reference_edges | integer | Shared edges with top_strength_reference |
| jaccard_with_reference_edges | float | Jaccard overlap with top_strength_reference |
| overlap_with_consensus_edges | integer | Shared edges with threshold_path_consensus |
| jaccard_with_consensus_edges | float | Jaccard overlap with threshold_path_consensus |
| interpretation_label | string | high_overlap / moderate_overlap / low_overlap / reference |

---

## Field list: bmc13_pairwise_overlap_summary.csv

| field | type | description |
|---|---|---|
| method_a | string | First method |
| method_b | string | Second method |
| edges_a | integer | Edge count of first method |
| edges_b | integer | Edge count of second method |
| shared_edges | integer | Number of shared edges |
| union_edges | integer | Number of union edges |
| jaccard | float | Jaccard overlap |

---

## Conservative interpretation template

### Befund

BMC-13 compares the N=81 BMC09d/BMC-12f reference anchor against alternative backbone extraction rules.

### Interpretation

High overlap across conceptually different methods would strengthen the interpretation of the N=81 anchor as a method-crossing sparse/local structure. Low overlap would indicate that the current anchor is specific to the top-strength extraction family.

### Hypothesis

If alternative methods recover a shared core, the N=81 anchor may represent a persistent relational locality-backbone candidate rather than only a top-strength artifact.

### Open gap

BMC-13 is still a graph-method diagnostic. It does not establish physical spacetime emergence or geometry reconstruction.
