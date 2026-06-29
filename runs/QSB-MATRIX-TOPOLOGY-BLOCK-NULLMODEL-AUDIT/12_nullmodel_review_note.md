# QSB-MATRIX-TOPOLOGY-BLOCK-NULLMODEL-AUDIT

## Source basis

This run uses the EXTRACT03 edge-candidate table and the confirmed closure, block-structure, and block-semantics audit summaries listed in `02_block_nullmodel_audit_scope.md`. Strength-profile context was present: True.

## Method

The observed candidate graph was reconstructed as an undirected graph on the 42 Pair-ID nodes. Three graph-theoretic controls were run with deterministic seeds: fixed edge-count `G(n,m)`, degree-preserving double-edge swaps, and fixed block-size semantic randomization.

## Observed graph

The observed graph has 42 nodes, 861 possible undirected edges, 161 candidate edges, component sizes [12, 10, 8, 6, 4, 2], 420 triangles, 0 open wedges, and global closure ratio 1.0.

## Nullmodel 1: fixed edge count G(n,m)

Trials: 10000. Hits for complete disjoint clique blocks: 0. Hits for exact semantic block edge set: 0. Plus-one p-values are reported in `11_nullmodel_pvalue_report.csv`.

## Nullmodel 2: degree-preserving edge swaps

Trials: 2000. Edge-swap attempts per trial: 5000. Hits for complete disjoint clique blocks: 0. Hits for exact semantic block edge set: 0.

## Nullmodel 3: semantic block randomization

Trials: 10000. Exact semantic block match count: 0. This control preserves the six block sizes and clique construction while randomizing node assignment.

## Results

The nullmodel status is `observed_block_structure_rare_under_tested_nullmodels`. Zero-hit tests are not reported as `p=0`; plus-one estimates and zero-hit upper bounds are reported.

## Interpretation

This run tests rarity under the specified graph-theoretic nullmodels. The result is only as strong as those nullmodels. It does not establish a general rarity proof outside these controls.

## Claim boundary

This is a structural, graph-theoretic, index-semantic, and statistically descriptive audit only. It makes no physical, geometric, metric, gravitative, causal, dynamical, experimental, or physical-emergence interpretation.

## Next-step gate

Any later use of these results should cite the tested nullmodels, trial counts, deterministic seeds, and plus-one p-value convention. Further interpretation requires separate evidence and separate review.
