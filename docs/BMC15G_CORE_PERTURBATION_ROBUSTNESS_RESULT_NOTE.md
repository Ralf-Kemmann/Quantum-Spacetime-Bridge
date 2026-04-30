# BMC-15g Core Perturbation Robustness — Result Note

## 1. Purpose

BMC-15g tests whether the compact BMC-15 reference-core proxy remains recoverable under small controlled perturbations of the canonical relational graph object.

This block is a robustness diagnostic. It does not claim physical spacetime geometry, causal structure, Lorentzian structure, uniqueness, or a continuum limit.

## 2. Run context

The run used the BMC-15 graph-object exports as reference material:

- source graph: `runs/BMC-15/geometry_proxy_diagnostics_open/graph_objects/N81_full_baseline_edges.csv`
- reference core: `runs/BMC-15/geometry_proxy_diagnostics_open/graph_objects/top_strength_reference_core_edges.csv`
- reference envelopes:
  - `maximum_spanning_tree_envelope_edges.csv`
  - `mutual_kNN_k3_envelope_edges.csv`
  - `threshold_path_consensus_envelope_edges.csv`

Output directory:

```text
runs/BMC-15g/core_perturbation_robustness_open/
```

Observed output sizes:

```text
perturbation_metrics.csv:      1800 metric rows
envelope_overlap_summary.csv:  5400 envelope rows
```

This matches the configured design:

```text
3 perturbation families
× 4 strengths
× 3 seeds
× 50 repeats
= 1800 core metric rows

1800 core rows
× 3 reference envelopes
= 5400 envelope rows
```

## 3. Perturbation families

BMC-15g used three perturbation families:

1. `edge_dropout`  
   Randomly removes a small fraction of graph edges.

2. `edge_swap`  
   Randomly removes a small fraction of graph edges and inserts the same number of random non-edges among the existing node set.

3. `weight_jitter`  
   Applies multiplicative log-normal jitter to existing edge weights:

```text
w' = w * exp(N(0, sigma))
```

The candidate core was reconstructed by selecting the strongest `m_core` edges in each perturbed graph, where `m_core` equals the number of edges in the reference core.

## 4. Primary family-level results

### 4.1 Edge dropout

| strength | n | mean core edge retention | min | max | mean edge Jaccard | mean node retention | connected fraction |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 0.01 | 150 | 0.9844 | 0.8333 | 1.0000 | 0.9733 | 0.9896 | 1.0000 |
| 0.03 | 150 | 0.9711 | 0.6667 | 1.0000 | 0.9510 | 0.9807 | 1.0000 |
| 0.05 | 150 | 0.9533 | 0.6667 | 1.0000 | 0.9205 | 0.9696 | 1.0000 |
| 0.10 | 150 | 0.8900 | 0.6667 | 1.0000 | 0.8205 | 0.9304 | 1.0000 |

### 4.2 Edge swap

| strength | n | mean core edge retention | min | max | mean edge Jaccard | mean node retention | connected fraction |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 0.01 | 150 | 0.9844 | 0.8333 | 1.0000 | 0.9733 | 0.9896 | 1.0000 |
| 0.03 | 150 | 0.9711 | 0.6667 | 1.0000 | 0.9510 | 0.9822 | 1.0000 |
| 0.05 | 150 | 0.9533 | 0.6667 | 1.0000 | 0.9205 | 0.9733 | 1.0000 |
| 0.10 | 150 | 0.8900 | 0.6667 | 1.0000 | 0.8205 | 0.9326 | 1.0000 |

### 4.3 Weight jitter

| strength | n | mean core edge retention | min | max | mean edge Jaccard | mean node retention | connected fraction |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 0.01 | 150 | 0.8000 | 0.5000 | 1.0000 | 0.6802 | 0.8800 | 1.0000 |
| 0.03 | 150 | 0.6367 | 0.3333 | 1.0000 | 0.4830 | 0.7733 | 1.0000 |
| 0.05 | 150 | 0.5644 | 0.1667 | 1.0000 | 0.4108 | 0.7304 | 1.0000 |
| 0.10 | 150 | 0.4811 | 0.0000 | 0.8333 | 0.3294 | 0.6778 | 1.0000 |

## 5. Containment-label results

### 5.1 Edge dropout

| strength | high | moderate | low | weak |
|---:|---:|---:|---:|---:|
| 0.01 | 150 | 0 | 0 | 0 |
| 0.03 | 149 | 1 | 0 | 0 |
| 0.05 | 149 | 1 | 0 | 0 |
| 0.10 | 131 | 19 | 0 | 0 |

### 5.2 Edge swap

| strength | high | moderate | low | weak |
|---:|---:|---:|---:|---:|
| 0.01 | 150 | 0 | 0 | 0 |
| 0.03 | 149 | 1 | 0 | 0 |
| 0.05 | 149 | 1 | 0 | 0 |
| 0.10 | 131 | 19 | 0 | 0 |

### 5.3 Weight jitter

| strength | high | moderate | low | weak |
|---:|---:|---:|---:|---:|
| 0.01 | 105 | 43 | 2 | 0 |
| 0.03 | 28 | 72 | 42 | 8 |
| 0.05 | 15 | 54 | 56 | 25 |
| 0.10 | 4 | 31 | 66 | 49 |

## 6. Befund

BMC-15g shows a clear split between topological perturbations and weight-rank perturbations.

Under `edge_dropout` and `edge_swap`, the reconstructed core retains a high fraction of the reference-core edge set across all tested strengths. Even at strength `0.10`, mean core edge retention remains approximately `0.89`, with all runs remaining connected and no low or weak containment labels.

Under `weight_jitter`, core recovery degrades much more strongly. At strength `0.01`, mean edge retention is still `0.80`, but by strength `0.10` it falls to approximately `0.48`, with weak and low containment labels becoming common.

## 7. Interpretation

The compact BMC-15 reference-core proxy is robust under small topological perturbations in this test design. The core does not immediately disappear when a small fraction of edges is removed or lightly rewired.

However, the reconstruction rule is sensitive to weight-rank perturbations. This is expected because the BMC-15g candidate core is reconstructed by selecting the strongest `m_core` edges. Multiplicative jitter acts directly on the edge-weight ordering and can therefore reshuffle which edges enter the top-strength candidate core.

In internal language:

```text
Der Klunker bleibt bei leichtem Kanten-Rütteln ziemlich stabil.
Wenn man aber an den Gewichten rüttelt, sortiert sich die Schmuckschatulle teilweise neu.
```

## 8. Methodological caution

The equality of `edge_dropout` and `edge_swap` core-level values is noteworthy. It likely indicates that, for this specific top-strength core readout, the dominant effect is whether high-ranking core edges are removed. Newly inserted swap edges apparently do not usually enter the top-`m_core` candidate set.

This should not be overinterpreted as equivalence of the perturbation mechanisms. It is a property of this readout and this graph-object regime.

## 9. Envelope observations

The first inspected envelope-overlap rows show that broad envelope overlap can remain very high for the threshold-path-consensus envelope under small weight jitter, while smaller envelopes such as the maximum-spanning-tree and mutual-kNN references show more moderate overlap.

Illustrative initial rows at `weight_jitter = 0.01` show:

- maximum-spanning-tree envelope: edge retention around `0.7619`
- mutual-kNN-k3 envelope: edge retention around `0.8261` to `0.8696`
- threshold-path-consensus envelope: edge retention around `0.9714` to `1.0000`

This is consistent with a simple size effect and construction effect: broader envelopes have more opportunity to retain overlap, while smaller sparse envelopes are more sensitive to rank and construction changes.

A full envelope-level family aggregation should be added if BMC-15g is extended or used in an external-facing note.

## 10. Conservative conclusion

BMC-15g supports a construction-qualified robustness statement for the compact BMC-15 reference-core proxy under small topological perturbations of the canonical graph object.

At the same time, BMC-15g identifies weight-rank sensitivity as an important methodological boundary of the current top-strength core reconstruction rule.

The strongest defensible statement is therefore:

```text
The local core proxy is topologically robust under small edge-level perturbations,
but its reconstruction remains sensitive to perturbations of the weight ranking.
```

This strengthens the internal BMC-15 geometry-proxy story as a robust methodological signal, while keeping the claim boundary intact.

## 11. Recommended next step

Before making BMC-15g outward-facing, add one compact envelope-level aggregate table from `envelope_overlap_summary.csv`, grouped by:

```text
perturbation_type
strength
reference_name
```

with mean/min/max values for:

```text
edge_retention_fraction
edge_jaccard
```

This will make the envelope part as auditable as the core-retention part.
