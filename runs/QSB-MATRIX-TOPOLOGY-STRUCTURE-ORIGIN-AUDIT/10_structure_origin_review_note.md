# QSB-MATRIX-TOPOLOGY-STRUCTURE-ORIGIN-AUDIT

## Source basis

This run uses the EXTRACT03 edge-candidate artifact and the prior closure, block-structure, block-semantics, block-strength, and nullmodel summaries listed in `02_structure_origin_audit_scope.md`.

## Method

The audit parsed Pair-IDs into integer index distances, tested row-wise equivalence between candidate flags, thresholding, `strength == 1.0`, and shared `abs_delta`, inventoried upstream text traces, and ran deterministic Pair-label permutations.

## Data-level rule equivalence

At artifact level, `edge_candidate_flag` is equivalent to shared Pair-ID `abs_delta`: True. `strength == 1.0` is equivalent to shared `abs_delta`: True. Mismatch count: 0.

## Strength and threshold relation

At artifact level, `edge_candidate_flag` is equivalent to `strength >= theta_edge`: True. Within same-abs-delta strengths range from 1.0 to 1.0; cross-abs-delta strengths range from 0.006936140120339703 to 0.34091958020143315. Theta range: 0.5 to 0.5.

## Pair-label permutation probe

Permutation trials: 1000. Exact rule-preserved count: 0. Plus-one p-value: 0.000999000999000999. This probes label binding of the current Pair-ID distance semantics; it is not a recomputation of upstream candidate generation.

## Upstream trace inventory

Trace status: `upstream_rule_trace_unresolved`. The inventory records file/header/lineage information, run-directory files, and bounded text matches. Text matches are trace evidence only and are not treated as a full upstream rule proof unless explicitly reconstructed.

## Interpretation

The observed clique-block structure is genuine in the candidate graph, but at the current artifact level it is constructively explained by the equivalence between candidate edges and shared Pair-ID index-distance classes. This makes it a robust rule-structured relational pattern, not an independent spacetime or physics claim.

The upstream origin is only stated at the level supported by the trace inventory. If the upstream trace is partial or unresolved, this audit does not claim that the source generation rule has been fully proven from upstream code.

## Claim boundary

This audit is methodical, structural, graph-theoretic, and data-lineage oriented. It makes no physical, geometric, metric, gravitative, causal, dynamical, experimental, or physical-emergence interpretation.

## Next-step gate

Further work should distinguish artifact-level equivalence from upstream rule reconstruction. A stronger origin claim would require direct review of the exact generator path that writes `16_edge_candidate_result.csv`.
