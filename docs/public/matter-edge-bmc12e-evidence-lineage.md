# Matter–Edge/BMC-12e evidence lineage

## Scientific chain

```text
calibration
→ holdout
→ association nulls
→ node-state nulls
→ null-model review
→ finalize
→ finalize review
→ PostgreSQL DWH ingest
→ DWH-ingest review
→ public surface
```

## Closed result

```text
decision=no_structural_consistency_detected
scientific_result_class=closed_negative_structural_consistency_result
```

## Source run identifiers

```text
null_execution=QSB-MATTER-EDGE-BMC12E-CONSISTENCY-EXECUTION-NULL-MODELS-EXECUTION-01
finalize=QSB-MATTER-EDGE-BMC12E-CONSISTENCY-EXECUTION-FINALIZE-01
dwh_ingest=QSB-MATTER-EDGE-BMC12E-CONSISTENCY-EXECUTION-DWH-INGEST-01
dwh_review=QSB-MATTER-EDGE-BMC12E-CONSISTENCY-EXECUTION-DWH-INGEST-REVIEW-01
```

## Reviewed artifact hashes

```text
null_execution_final_status_sha256=0d0aa50748c0de15c635389d9605b46ce22fd360f9559452b873f931a763b979
finalize_summary_sha256=33a072d058010956e501977b1c73137e27b937a5acfa0b14b56c3c4998b2cf90
dwh_ingest_final_status_sha256=c28985f27824870510479fba3301a7881b2f7a35d0e9a01a6256980390525514
dwh_review_final_status_sha256=8e80ea903060f2516e8683f5fac5e52fa4baeb0c024c8db1dd69cadb15573bf0
```

## Claim boundary

The lineage supports only a negative structural-consistency result for
the frozen tested mapping. It does not support a physics claim, mechanism
claim, anti-mechanism claim, or general falsification of the Matter–Edge
model family.
