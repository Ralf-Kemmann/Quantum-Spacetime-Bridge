# Matter–Edge/BMC-12e consistency result

## Status

```text
decision=no_structural_consistency_detected
scientific_result_class=closed_negative_structural_consistency_result
physical_claim_release=blocked_no_physics_claim
mechanism_claim_release=blocked_no_mechanism_claim
manuscript_integration_authorized=false
```

## Result

Under the frozen state-preparation, graph, backbone, readout, decision,
and null-model contracts, the dimensionless Matter–Edge response did not
reproduce the BMC-12e localization pattern out of sample.

This is a closed negative structural-consistency result for the tested
mapping. It is not a physical falsification, not a general rejection of
Matter–Edge toy models, and not an anti-mechanism claim.

## Frozen evaluation

The selected dimensionless response scale was:

```text
lambda_star=1e-06
```

The pooled holdout endpoints were:

| Endpoint | Observed value |
|---|---:|
| Spearman rho | -0.003419279020221768 |
| Four-class Macro-F1 | 0.2209348198970841 |

The preregistered upper-tail null results were:

| Null family | Spearman upper p | Macro-F1 upper p |
|---|---:|---:|
| Within-N BMC outcome permutation | 0.5923407659234077 | 0.326967303269673 |
| Within-graph node-state permutation | 0.9637036296370363 | 0.8401159884011599 |

Neither co-primary endpoint showed positive upper-tail extremeness under
either null family. The null models therefore did not rescue the adverse
calibration or the non-supportive holdout.

## Evidence volume

```text
null_permutation_rows=20000
seed_audit_rows=240000
batch_manifest_rows=200
association_permutations=10000
node_state_permutations=10000
```

The full BMC-12e edge-count sweep is the scientific anchor. N=81 remains
the central reference configuration within that controlled result space;
it is not claimed to be uniquely optimal.

## Repair disclosure

Two execution-path repairs were required and preserved in lineage:

1. Metric-input normalization of the known raw label
   `off_backbone_localization_supported` to the frozen class
   `full_only_or_mixed`.
2. Restoration of missing completion-document files after all null
   permutations had already completed.

Neither repair changed the model, selected lambda, seeds, permutation
policy, metric definitions, scientific outputs, or claim boundaries.

## Reproducibility and provenance

The result was finalized only after independent null-model execution
review, finalize review, PostgreSQL DWH ingest, and DWH-ingest review.

Reviewed source hashes:

```text
null_execution_final_status_sha256=0d0aa50748c0de15c635389d9605b46ce22fd360f9559452b873f931a763b979
finalize_summary_sha256=33a072d058010956e501977b1c73137e27b937a5acfa0b14b56c3c4998b2cf90
dwh_ingest_final_status_sha256=c28985f27824870510479fba3301a7881b2f7a35d0e9a01a6256980390525514
dwh_review_final_status_sha256=8e80ea903060f2516e8683f5fac5e52fa4baeb0c024c8db1dd69cadb15573bf0
```

## Human–AI methods note

Human scientific judgment defined the research question, frozen
contracts, admissible decision rules, claim boundaries, and final
interpretation. AI-assisted workflows supported code generation,
metadata structuring, consistency checks, and artifact review. Negative
and neutral results were retained rather than optimized away, and every
public statement remains bounded by the independently reviewed evidence.
