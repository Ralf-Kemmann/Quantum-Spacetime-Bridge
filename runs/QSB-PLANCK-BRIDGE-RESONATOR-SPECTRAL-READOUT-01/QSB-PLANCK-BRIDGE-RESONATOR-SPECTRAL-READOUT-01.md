# QSB-PLANCK-BRIDGE-RESONATOR-SPECTRAL-READOUT-01

## Befund

This run reads the existing `K_candidate` matrix and recomputes spectral diagnostics with `numpy.linalg.eigvalsh`.

The matrix is tested as a formal Gram-structure object. Pair identifiers of the form `i|j` are parsed as directed differences over seven base indices. The readout records rank, nullity, trace, positive eigenvalue mass, lag-class membership, parallel pairs, antiparallel pairs, and an effective 6 x 6 lag-axis Gram summary.

## Interpretation

The K_candidate matrix is PSD within numerical tolerance and exhibits a rank-6 directed lag-class structure. This supports only a formal Gram-structure readout and leaves all physics claims blocked.

The 42 directed pair-features are consistent with `7 * 6 = 42` directed pairs without diagonal entries. Under the observed Gram structure, they collapse formally into 6 effective lag axes, with opposite directions treated as antiparallel.

## Hypothese

The rank-6 result is consistent with a directed pair-difference construction over seven base indices.

## Offene Luecke

This run does not provide a physical model, empirical status, continuum limit, dynamics, or uniqueness proof. Human review remains required before downstream interpretation.

## Claim Boundary

- `claim_status = formal_matrix_structure_readout_only`
- `physical_claim_release = blocked_no_physics_claim`
- `review_status = requires_human_review`

The spectral readout supports only a formal matrix-structure statement:
the K_candidate matrix is consistent with a rank-6 directed lag-class Gram structure.
All physical claims remain blocked.

