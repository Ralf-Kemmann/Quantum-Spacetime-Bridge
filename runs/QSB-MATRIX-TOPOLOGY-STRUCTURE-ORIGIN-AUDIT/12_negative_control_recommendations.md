# Negative Control Recommendations

- Source-/rule-ablation: recompute candidate edges with any Pair-ID distance component removed or masked.
- Label-permuted recomputation: rerun the upstream generator after permuting labels before candidate generation, not only after artifact creation.
- Alternative Pair-ID construction: test whether a different Pair-ID indexing scheme produces the same candidate relation.
- Theta sweeps: vary `theta_edge` and check whether the block structure persists or changes predictably.
- Independent source matrix: compare against a matrix not generated from the same Pair-ID distance logic.
- Upstream quantity comparison: if validated source quantities exist, compare candidate flags against those quantities independently of Pair-ID labels.

These are recommendations only and make no physics claim.
