# Implementation Plan Before Patch

## Scope

Implement only QSB/PBR Matrix Construction Contract infrastructure:

- a scoped K-only callable/wrapper under `scripts/qsb_pbr_matrix_contract/`
- explicit contract field exports
- lag-class handoff declaration exports
- randomization-control policy declaration exports
- validation harness for contract readiness
- documentation describing usage and limits

## Files Planned

New repository files:

- `scripts/qsb_pbr_matrix_contract/__init__.py`
- `scripts/qsb_pbr_matrix_contract/reconstruct_k_candidate.py`
- `docs/QSB_PBR_MATRIX_CONTRACT_SOURCE_PATCH_IMPLEMENTATION.md`

New run-package files:

- required CSV, docs, validation, and report artifacts under `runs/QSB-PLANCK-BRIDGE-RESONATOR-MATRIX-CONSTRUCTION-CONTRACT-SOURCE-PATCH-IMPLEMENTATION-01/`

## Existing Files

No historical EXTRACT03A-R1 source file will be modified.

## Non-Scope

No Lag-Class Sufficiency Execution 01A, nullmodel, spectral interpretation, DWH write, literature import, candidate repair, candidate upgrade, physics claim, or mechanism claim.
