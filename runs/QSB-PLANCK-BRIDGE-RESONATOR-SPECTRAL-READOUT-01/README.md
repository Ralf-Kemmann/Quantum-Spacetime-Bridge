# QSB-PLANCK-BRIDGE-RESONATOR-SPECTRAL-READOUT-01

This run package performs a formal spectral readout of the existing `K_candidate` matrix after the registered PSD gate passed.

The readout is limited to matrix structure. It does not release physical, empirical, continuum-limit, or ontology claims.

## Inputs

- Matrix: `runs/QSB-EXTRACT03A-R1/authorized_execution_with_s1_addendum/11_K_candidate_matrix.csv`
- Prior PSD validation: `runs/QSB-EXTRACT03A-R1/authorized_execution_with_s1_addendum/12_K_validation_results.csv`
- Prior runs:
  - `runs/QSB-PLANCK-BRIDGE-RESONATOR-STATE-SPEC-01/`
  - `runs/QSB-PLANCK-BRIDGE-RESONATOR-PSD-TEST-01/`

## Claim Boundary

- `claim_status = formal_matrix_structure_readout_only`
- `physical_claim_release = blocked_no_physics_claim`
- `review_status = requires_human_review`

The spectral readout supports only a formal matrix-structure statement:
the K_candidate matrix is consistent with a rank-6 directed lag-class Gram structure.
All physical claims remain blocked.

