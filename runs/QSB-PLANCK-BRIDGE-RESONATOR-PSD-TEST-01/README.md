# QSB-PLANCK-BRIDGE-RESONATOR-PSD-TEST-01

This run package re-evaluates the existing `K_candidate` matrix from `QSB-EXTRACT03A-R1` under the PBR-State-Spec Gram/PSD admissibility gate.

The matrix is tested only as a formal Gram-candidate under the registered PBR State Spec. The allowed result is limited to whether the matrix passes or fails the minimal Gram/PSD admissibility gate within the stated numerical tolerance.

## Inputs

- Matrix: `runs/QSB-EXTRACT03A-R1/authorized_execution_with_s1_addendum/11_K_candidate_matrix.csv`
- Prior validation: `runs/QSB-EXTRACT03A-R1/authorized_execution_with_s1_addendum/12_K_validation_results.csv`
- State spec run: `runs/QSB-PLANCK-BRIDGE-RESONATOR-STATE-SPEC-01/`

## Claim Boundary

- `claim_status = formal_admissibility_result_only`
- `physical_claim_release = blocked_no_physics_claim`
- `review_status = requires_human_review`

This package does not release physical, empirical, continuum-limit, or ontology claims.

