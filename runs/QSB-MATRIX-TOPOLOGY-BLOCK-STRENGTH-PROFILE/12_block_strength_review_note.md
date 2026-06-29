# QSB-MATRIX-TOPOLOGY-BLOCK-STRENGTH-PROFILE

## Source basis

This run uses the EXTRACT03 edge-candidate table and the confirmed closure, block-structure, and block-semantics audit summaries listed in `02_block_strength_profile_scope.md`.

## Method

Each edge row was enriched with component and Pair-ID distance-class metadata from the semantics audit. Rows were separated into `within_confirmed_block` and `between_confirmed_blocks`, then profiled by component, component pair, abs-delta pair, threshold-margin category, and strongest observed rows.

## Results

- Edge rows total: 861
- Candidate edge count: 161
- Non-candidate edge count: 700
- Within-block rows: 161
- Between-block rows: 700
- All within-block rows candidates: True
- All between-block rows non-candidates: True
- Strength profile status: `strength_profile_consistent_with_confirmed_block_structure`

## Internal block strength profile

Within confirmed blocks, the observed strength range is 1.0 to 1.0, with median 1.0 and mean 1.0. The internal components ordered by mean strength are recorded in `04_block_strength_summary.json`.

## Cross-block strength profile

Between confirmed blocks, the observed strength range is 0.006936140120339703 to 0.34091958020143315, with median 0.18664400870287967 and mean 0.16673021799110121. The strongest cross-block row has strength 0.34091958020143315 and margin -0.15908041979856685.

## Threshold-margin observations

Threshold margins are available for this run: True. Within-block margins range from 0.5 to 0.5. Between-block margins range from -0.4930638598796603 to -0.15908041979856685.

## Interpretation

This run numerically describes the edge weights of the already confirmed block structure. It checks whether candidate edges inside confirmed distance-class blocks can also be characterized as a weighted structure, and whether cross-block non-candidate edges lie near or below the threshold.

The result is descriptive only. It does not provide a physical, geometric, metric, gravitative, causal, dynamical, experimental, or physical-emergence interpretation.

## Claim boundary

The `strength` values are treated only as numeric edge weights from the existing EXTRACT03 candidate logic. This note makes no claim about physical geometry, spacetime, metric structure, gravitation, causality, dynamics, experimental validation, or physical emergence.

## Next-step gate

Any later use of these strength profiles should cite this run directory and keep the numeric descriptive claim boundary explicit. Further interpretation would require separate evidence and separate review.
