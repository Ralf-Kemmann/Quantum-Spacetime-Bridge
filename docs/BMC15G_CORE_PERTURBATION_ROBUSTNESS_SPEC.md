# BMC-15g Core Perturbation Robustness — Specification

## Purpose

BMC-15g tests whether the compact reference-core signal observed in the BMC-15 geometry-proxy layer remains recoverable under small controlled perturbations of the relational graph object.

This is a **robustness diagnostic**. It does **not** claim physical spacetime geometry, causal/Lorentzian structure, uniqueness, or a continuum limit.

## Methodological role

BMC-15e/f/f1/f2 established construction-qualified geometry-proxy and envelope-readout behavior. BMC-15g asks a narrower question:

> If the canonical relational graph is slightly perturbed, does a reconstructed top-strength core of the same edge count continue to overlap the observed reference core?

## Inputs

Recommended canonical inputs:

- `runs/BMC-15/geometry_proxy_diagnostics_open/graph_objects/N81_full_baseline_edges.csv`
- `runs/BMC-15/geometry_proxy_diagnostics_open/graph_objects/top_strength_reference_core_edges.csv`
- optional reference envelopes:
  - `maximum_spanning_tree_envelope_edges.csv`
  - `mutual_kNN_k3_envelope_edges.csv`
  - `threshold_path_consensus_envelope_edges.csv`

## Perturbation families

- `weight_jitter`: existing edge weights are multiplied by `exp(N(0, sigma))`.
- `edge_dropout`: a small fraction of edges is removed.
- `edge_swap`: a small fraction of edges is removed and replaced by random non-edges with sampled removed weights.

## Core reconstruction rule

For each perturbed graph, the candidate core is defined as the strongest `m_core` edges, where `m_core` equals the number of reference-core edges.

## Outputs

Default output directory:

```text
runs/BMC-15g/core_perturbation_robustness_open/
```

Files:

- `summary.json`
- `perturbation_metrics.csv`
- `family_summary.csv`
- `core_retention_summary.csv`
- `envelope_overlap_summary.csv`
- `readout.md`

## Conservative containment labels

- `core_retention_high`: edge-retention fraction >= 0.80
- `core_retention_moderate`: >= 0.60 and < 0.80
- `core_retention_low`: >= 0.40 and < 0.60
- `core_retention_weak`: < 0.40

These bins are descriptive only.

## Interpretation boundary

Favorable retention supports only a construction-qualified robustness statement for the local graph-core proxy. It cannot establish physical spacetime, a metric manifold, causal structure, Lorentzian behavior, or uniqueness.
