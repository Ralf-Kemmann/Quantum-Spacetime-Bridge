# QSB-MATRIX-TOPOLOGY-LABEL-PERMUTED-RECOMPUTE-CONTROL

## Purpose

This run performs a guarded label-permutation control after the upstream generator trace was resolved.

## Source Basis

Primary edge artifact: `runs/QSB-EXTRACT03A-R1/authorized_execution_with_s1_addendum/16_edge_candidate_result.csv`.

Generator script: `scripts/qsb_extract03a_r1/run_authorized_execution_with_s1_addendum.py`.

Prior trace status: `upstream_generator_trace_found`.

## Generator Dependency Profile

The generator rule is reconstructable from repository artifacts. The original generator has fixed output paths and an overwrite guard, so it was not run in place.

## Baseline Artifact Profile

The primary edge file has 861 rows, 161 candidate edges, and 700 non-candidate edges. The candidate flag matches `strength >= theta_edge` and matches original pair-id absolute-delta classes.

## Label Permutation

Seed: `20260630_label_permutation_control_v1`.

The permutation is deterministic and non-trivial over labels `0,1,2,3,4,5,6`.

## Post-Hoc Alignment

Original abs-delta alignment: `True`.

Permuted abs-delta alignment: `False`.

This establishes post-hoc label sensitivity of the artifact-level topology.

## Recompute Status

A true source-native isolated label-permuted recompute was not executed. The run includes a reconstructed-rule control only, derived from the resolved generator rule and the existing pair-label domain.

## Interpretation

The existing candidate topology follows the original label-derived abs-delta rule at artifact level. This is a methodological control result, not a source-signal or physics result.

## Claim Boundary

methodological control only; no physics, spacetime, gravity, causality, or source-signal claim

## Next-Step Gate

Recommended next run: `QSB-MATRIX-TOPOLOGY-ISOLATED-GENERATOR-WRAPPER-CONTROL`.
