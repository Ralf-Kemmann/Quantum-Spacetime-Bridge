# QSB/PBR Matrix Contract Source Patch Implementation

This document describes the scoped infrastructure added for the QSB/PBR Matrix Construction Contract.

Implemented command:

```bash
python scripts/qsb_pbr_matrix_contract/reconstruct_k_candidate.py --mode export \
  --source-db runs/QSB-INTERFACE01F3/authorized_delta_phi_export_staging_preflight/09_delta_phi_staging_preflight.sqlite \
  --pair-basis runs/QSB-EXTRACT03-S1/split_seed_freeze_addendum/06_canonical_pair_basis_review.csv \
  --k-candidate runs/QSB-EXTRACT03A-R1/authorized_execution_with_s1_addendum/11_K_candidate_matrix.csv \
  --expected-k-sha256 e1acdf0acf31e2faf68f8a517cbdbccb2f9af9e28fe974eeb01c0a7f0928754d \
  --output-dir /tmp/qsb_pbr_matrix_contract_export
```

The command exports contract-field, lag-class-handoff, and control-policy declaration artifacts, then validates hashes, schemas, explicit placeholders, hidden-state guard metadata, and claim boundaries.

The command does not authorize Execution 01A, does not run Lag-Class Sufficiency, does not execute nullmodels, does not write to DWH, and does not create physical or mechanism claims.
