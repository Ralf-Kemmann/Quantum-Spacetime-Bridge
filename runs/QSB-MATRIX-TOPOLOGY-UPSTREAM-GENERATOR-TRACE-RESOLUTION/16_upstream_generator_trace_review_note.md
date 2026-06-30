# QSB-MATRIX-TOPOLOGY-UPSTREAM-GENERATOR-TRACE-RESOLUTION

## Purpose

This audit resolves whether the observed artifact-level rule structure can be traced to an upstream generator in the repository. It does not by itself establish a source-driven signal; it determines whether replay and recomputation controls are now feasible.

## Source basis

Primary edge file: `runs/QSB-EXTRACT03A-R1/authorized_execution_with_s1_addendum/16_edge_candidate_result.csv`. Context was read from prior origin and source-signal gate artifacts when present.

## Primary edge file profile

The primary edge artifact exists: True. It has 861 rows, 161 candidate edges, and 700 non-candidate edges.

## Trace search method

The search was curated to EXTRACT03 scripts, package contracts, A-R1 run artifacts, and downstream review scripts. Large raw grep dumps were not written.

## Generator candidate files

The direct generator candidate is `scripts/qsb_extract03a_r1/run_authorized_execution_with_s1_addendum.py`.

## Direct output writer evidence

The direct generator defines the output filename list containing `16_edge_candidate_result.csv`, constructs `edge_rows`, and calls `write_csv(FILES[15], ...)`.

## Strength generation trace

The generator computes `strength = np.exp(-d / ELL_0)` after constructing `d` from `K` and writes `15_strength_matrix.csv` as `relation_strength`.

## Theta-edge trace

The generator defines `THETA_EDGE = 0.5` and checks the frozen HF-06 decision before execution. The primary edge artifact carries `theta_edge=0.5`.

## Edge-candidate-flag trace

The generator computes `edge = strength >= THETA_EDGE`, clears the diagonal, and writes `edge_candidate_flag` as `int(edge[i,j])`.

## Lineage and manifest trace

The A-R1 manifest records the lineage payload and `lineage_bundle_sha256`. The lineage/hash audit records output hashes including `16_edge_candidate_result.csv`.

## Reconstruction assessment

Upstream trace status: `upstream_generator_trace_found`. Generator rule status: `generator_rule_reconstructable_from_repo_artifacts`. Replay is methodologically feasible from repo artifacts, but the original script refuses to overwrite the existing A-R1 run and uses fixed output paths, so replay should be done via an isolated sanity-check wrapper or controlled copy.

## Recompute-control feasibility

Artifact-level threshold sweep is feasible. Label-permuted recompute, abs-delta masking, rule ablation, and source-signal controls require a separate controlled recompute design.

## Interpretation

The generator and core rule are traceable in repo artifacts. This resolves the prior upstream-generator blocker at the provenance/rule level, but it does not confirm a source-driven signal.

## Claim boundary

This is a provenance, lineage, and generator-trace audit only. It makes no physical, geometric, metric, gravitative, causal, dynamical, source-signal, experimental, or physical-emergence claim.

## Next-step gate

Recommended next run: `QSB-MATRIX-TOPOLOGY-LABEL-PERMUTED-RECOMPUTE-CONTROL`.
