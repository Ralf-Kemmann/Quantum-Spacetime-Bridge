# QSB-MATRIX-TOPOLOGY-LABEL-PERMUTED-RECOMPUTE-CONTROL

## Purpose

Run a guarded label-permutation control after upstream generator trace resolution.

## Source basis

- Primary edge file: `runs/QSB-EXTRACT03A-R1/authorized_execution_with_s1_addendum/16_edge_candidate_result.csv`
- Generator script: `scripts/qsb_extract03a_r1/run_authorized_execution_with_s1_addendum.py`
- Upstream trace summary: `runs/QSB-MATRIX-TOPOLOGY-UPSTREAM-GENERATOR-TRACE-RESOLUTION/04_upstream_generator_trace_summary.json`

## Execution boundary

This run does not modify existing EXTRACT03A-R1 outputs and does not run the original generator in place. The executed control is a baseline artifact sanity check plus deterministic post-hoc label-permutation alignment and a reconstructed-rule comparison.

## Claim boundary

methodological control only; no physics, spacetime, gravity, causality, or source-signal claim
