# QSB-MATRIX-TOPOLOGY-SOURCE-SIGNAL-SEPARATION-GATE

## Purpose

This gate separates the detector's ability to reveal structure from the stronger question of whether the structure is source-driven.

## Source basis

The gate reads the EXTRACT03 edge-candidate artifact and prior structure, semantics, strength, nullmodel, origin, and detector-generalization context where available.

## Rule/label/threshold controls

The prior origin audit confirms artifact-level equivalence between candidate edges and shared Pair-ID `abs_delta`, and between candidate flags and thresholded strength. This run reuses that boundary and profiles rule/label/threshold predictability.

## Available source-native artifacts

The EXTRACT03A-R1 folder contains pre-candidate matrices and lineage files. Their source-native status is not certified here; they are inventoried as available or unclear, not as independent source evidence.

## Residual signal after rule/label grouping

Residual profiles are produced after grouping by same-abs-delta and label-derived abs-delta pairs. Cross-block strength variation exists at coarse grouping, but current artifacts do not certify it as source-native residual signal.

## Threshold sweep feasibility

Threshold sweep is feasible from existing `strength` and `theta_edge` columns at artifact level. It does not replace upstream recomputation.

## Label-permuted recomputation feasibility

Post-hoc label permutation is feasible, but true recomputation after label permutation is not feasible now because the upstream generator trace is unresolved.

## Source-signal classification

Current source-signal status: `source_signal_not_testable_from_current_artifacts`.
Current pattern-origin classification: `rule_induced_artifact_structure_source_signal_unresolved`.

## Interpretation

This gate separates the detector's ability to reveal structure from the stronger question of whether the structure is source-driven. For EXTRACT03, the candidate topology is already explained at artifact level by rule/label/threshold features; any source-signal claim requires upstream recomputation or independent source-native features.

## Claim boundary

This is a methodological source-signal separation gate. It makes no physical, geometric, metric, gravitative, causal, dynamical, experimental, or physical-emergence claim.

## Next-step gate

Recommended next run: `QSB-MATRIX-TOPOLOGY-UPSTREAM-GENERATOR-TRACE-RESOLUTION`.
