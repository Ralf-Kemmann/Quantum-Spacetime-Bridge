# QSB-PLANCK-BRIDGE-RESONATOR-PSD-TEST-01

## Befund

This package recomputes Gram/PSD diagnostics for the existing `K_candidate` matrix from `QSB-EXTRACT03A-R1` using `numpy.linalg.eigvalsh`.

The test reconstructs the matrix from `row_pair_id`, `column_pair_id`, `K_candidate`, and `lineage_bundle_sha256`, then records square-shape, finite-value, symmetry, diagonal, eigenvalue, negative-eigenvalue, and PSD gate diagnostics.

## Interpretation

The result is interpreted only as a formal admissibility result under the PBR-State-Spec minimal Gram reading. A pass means that this matrix is not excluded by the registered numerical Gram/PSD gate at the stated tolerance. A fail means that this matrix fails that formal gate or needs modification before that reading can be used.

## Hypothese

If the recomputed matrix is square, finite, symmetric within tolerance, diagonal-normalized within tolerance, and has no eigenvalue below `-1e-10`, then the minimal formal Gram-candidate reading remains admissible for this input matrix.

## Offene Luecke

This run does not certify a physical model, empirical status, continuum limit, dynamical law, or uniqueness statement. Human review remains required for interpretation and downstream use.

## Claim Boundary

- `claim_status = formal_admissibility_result_only`
- `physical_claim_release = blocked_no_physics_claim`
- `review_status = requires_human_review`

Only the minimal Gram/PSD admissibility gate is evaluated.

