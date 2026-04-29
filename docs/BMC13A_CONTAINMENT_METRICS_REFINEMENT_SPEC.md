# BMC-13a Containment Metrics Refinement Specification

## Purpose

BMC-13a refines the interpretation of BMC-13 by adding containment metrics.

BMC-13 compared several alternative backbone extraction methods:

```text
top_strength_reference
mutual_kNN_k3
maximum_spanning_tree
threshold_path_consensus_min3
```

The initial BMC-13 summary used Jaccard overlap as the main comparison metric. This is useful but incomplete when the reference backbone is much smaller than the alternative backbones.

The top-strength reference core has only:

```text
6 edges
```

while the alternative methods produce larger envelopes:

```text
maximum_spanning_tree: 21 edges
mutual_kNN_k3: 23 edges
threshold_path_consensus_min3: 70 edges
```

In this case, Jaccard overlap can look small even if the entire reference core is contained in a larger method.

---

## New metrics

BMC-13a adds:

```text
reference_edge_count
reference_containment
method_containment
consensus_edge_count
consensus_containment
method_vs_consensus_containment
containment_label
```

Definitions:

```text
reference_containment = overlap_with_reference_edges / reference_edge_count
method_containment    = overlap_with_reference_edges / method_edge_count
```

Interpretation:

```text
reference_containment = 1.000
```

means the full reference core is contained in the method.

```text
method_containment < 1.000
```

means the method contains additional structure beyond the reference core.

---

## Expected interpretation

If all alternative methods have:

```text
reference_containment = 1.000
```

then the correct interpretation is not:

```text
low overlap with the reference
```

but rather:

```text
full containment of the reference core inside larger method-specific envelopes
```

---

## Output files

BMC-13a writes:

```text
runs/BMC-13/alternative_backbone_consensus_open/bmc13a_method_summary_with_containment.csv
runs/BMC-13/alternative_backbone_consensus_open/bmc13a_containment_readout.md
runs/BMC-13/alternative_backbone_consensus_open/bmc13a_metrics.json
```

---

## Conservative interpretation template

### Befund

The six-edge top-strength reference core is evaluated for containment inside alternative backbone constructions.

### Interpretation

Full reference containment across methods supports persistence of the small hard core. Differences in method size and Jaccard overlap indicate that the broader backbone envelope remains method-dependent.

### Hypothesis

The N=81 top-strength anchor may represent a compact core embedded within a larger relational backbone envelope.

### Open gap

BMC-13a is still a graph-method diagnostic and does not yet test physical geometry, causal structure, or continuum reconstruction.
